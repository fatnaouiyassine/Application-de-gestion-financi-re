from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os
from dotenv import load_dotenv
import random
import csv
from io import StringIO
from flask_migrate import Migrate

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # type: ignore
migrate = Migrate(app, db)
# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accounts = db.relationship('Account', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True)

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    account_type = db.Column(db.String(50), nullable=False)  # savings, checking, credit
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False)
    rib = db.Column(db.String(30), unique=True, nullable=False)
    transactions = db.relationship('Transaction', backref='account', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # income, expense
    date = db.Column(db.DateTime, default=datetime.utcnow)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.Date, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fundings = db.relationship('GoalFunding', backref='goal', lazy=True)

class GoalFunding(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey('goal.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader 
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registred', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email, password_hash=generate_password_hash(password))  # type: ignore
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    total_balance = sum(account.balance for account in accounts)
    recent_transactions = []
    for account in accounts:
        transactions = Transaction.query.filter_by(account_id=account.id).order_by(Transaction.date.desc()).limit(5).all()
        recent_transactions.extend(transactions)
    recent_transactions.sort(key=lambda x: x.date, reverse=True)
    recent_transactions = recent_transactions[:10]
    today_date = date.today()
    active_goals_count = sum(1 for goal in goals if goal.current_amount < goal.target_amount and goal.deadline >= today_date)
    return render_template('dashboard.html', 
                         accounts=accounts, 
                         goals=goals, 
                         total_balance=total_balance,
                         recent_transactions=recent_transactions,
                         today=today_date,
                         active_goals_count=active_goals_count)

@app.route('/accounts')
@login_required
def accounts():
    q = request.args.get('q', '').strip()
    account_type = request.args.get('account_type', '')
    min_balance = request.args.get('min_balance', '')
    max_balance = request.args.get('max_balance', '')
    sort_dir = request.args.get('sort_dir', 'asc')

    query = Account.query.filter_by(user_id=current_user.id)

    if q:
        query = query.filter(Account.name.ilike(f'%{q}%'))
    if account_type:
        query = query.filter(Account.account_type == account_type)
    if min_balance:
        try:
            query = query.filter(Account.balance >= float(min_balance))
        except ValueError:
            pass
    if max_balance:
        try:
            query = query.filter(Account.balance <= float(max_balance))
        except ValueError:
            pass

    # Only allow sorting by balance for now
    if sort_dir == 'desc':
        query = query.order_by(Account.balance.desc())
    else:
        query = query.order_by(Account.balance.asc())

    accounts = query.all()
    return render_template('accounts.html', accounts=accounts)

@app.route('/add_account', methods=['POST'])
@login_required
def add_account():
    name = request.form['name']
    account_type = request.form['account_type']
    initial_balance = float(request.form['initial_balance'])
    account_number = request.form['account_number']
    rib = request.form['rib']
    account = Account(name=name, account_type=account_type, 
                     balance=initial_balance, user_id=current_user.id,
                     account_number=account_number, rib=rib)
    db.session.add(account)
    db.session.commit()
    flash('Account created!')
    return redirect(url_for('accounts'))

@app.route('/edit_account/<int:account_id>', methods=['GET'])
@login_required
def edit_account(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('accounts'))
    return render_template('edit_account.html', account=account)

@app.route('/edit_account/<int:account_id>', methods=['POST'])
@login_required
def update_account(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('accounts'))
    account.name = request.form['name']
    account.account_type = request.form['account_type']
    account.balance = float(request.form['balance'])
    account.account_number = request.form['account_number']
    account.rib = request.form['rib']
    db.session.commit()
    flash('Account updated successfully!')
    return redirect(url_for('accounts'))

@app.route('/delete_account/<int:account_id>', methods=['POST'])
@login_required
def delete_account(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('accounts'))
    
    # Supprimer d'abord toutes les transactions associées
    Transaction.query.filter_by(account_id=account_id).delete()
    
    # Supprimer aussi les financements d'objectifs associés
    GoalFunding.query.filter_by(account_id=account_id).delete()
    
    # Maintenant supprimer le compte
    db.session.delete(account)
    db.session.commit()
    flash('Account deleted successfully!')
    return redirect(url_for('accounts'))

@app.route('/transactions/<int:account_id>')
@login_required
def transactions(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('accounts'))
    
    # Get filter/sort params
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    transaction_type = request.args.get('type', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    exact_date = request.args.get('exact_date', '')
    sort_by = request.args.get('sort_by', 'date')
    sort_dir = request.args.get('sort_dir', 'desc')

    query = Transaction.query.filter_by(account_id=account_id)

    if q:
        query = query.filter(Transaction.description.ilike(f'%{q}%'))
    if category:
        query = query.filter(Transaction.category == category)
    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)
    if exact_date:
        try:
            from datetime import datetime, timedelta
            date_obj = datetime.strptime(exact_date, '%Y-%m-%d')
            next_day = date_obj + timedelta(days=1)
            query = query.filter(Transaction.date >= date_obj, Transaction.date < next_day)
        except Exception:
            pass
    else:
        if start_date:
            from datetime import datetime
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Transaction.date >= start)
        if end_date:
            from datetime import datetime, timedelta 
            end = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Transaction.date < end)

    # Only allow sorting by date or amount
    if sort_by == 'amount':
        sort_column = Transaction.amount
    else:
        sort_column = Transaction.date
    if sort_dir == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    transactions = query.all()
    categories = sorted(list(set(t.category for t in Transaction.query.filter_by(account_id=account_id).all())))
    return render_template('transactions.html', account=account, transactions=transactions, categories=categories)

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    account_id = int(request.form['account_id'])
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('accounts'))
    
    amount = float(request.form['amount'])
    description = request.form['description']
    category = request.form['category']
    transaction_type = request.form['transaction_type']
    
    transaction = Transaction(amount=amount, description=description,
                            category=category, transaction_type=transaction_type,
                            account_id=account_id)
    
    # Update account balance
    if transaction_type == 'income':
        account.balance += amount
    else:
        account.balance -= amount
    
    db.session.add(transaction)
    db.session.commit()
    
    flash('Transaction added successfully! =')
    return redirect(url_for('transactions', account_id=account_id))

@app.route('/goals')
@login_required
def goals():
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    return render_template('goals.html', goals=goals, accounts=accounts, today=date.today())

@app.route('/add_goal', methods=['POST'])
@login_required
def add_goal():
    name = request.form['name']
    target_amount = float(request.form['target_amount'])
    deadline = datetime.strptime(request.form['deadline'], '%Y-%m-%d').date()
    category = request.form['category']
    
    goal = Goal(name=name, target_amount=target_amount, deadline=deadline,
                category=category, user_id=current_user.id)
    db.session.add(goal)
    db.session.commit()
    
    flash('Goal created!')
    return redirect(url_for('goals'))

@app.route('/update_goal_progress/<int:goal_id>', methods=['POST'])
@login_required
def update_goal_progress(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('goals'))
    if goal.current_amount >= goal.target_amount:
        flash('Goal already reached!', 'error')
        return redirect(url_for('goals'))
    additional_amount = float(request.form['additional_amount'])
    account_id = int(request.form['account_id'])
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Invalid account selected', 'error')
        return redirect(url_for('goals'))
    if account.balance < additional_amount:
        flash('Insufficient funds in selected account', 'error')
        return redirect(url_for('goals'))
    # Subtract from account
    account.balance -= additional_amount
    # Add to goal, but do not exceed target_amount
    amount_to_add = min(additional_amount, goal.target_amount- goal.current_amount)
    goal.current_amount += amount_to_add
    # Record the funding
    funding = GoalFunding(goal_id=goal.id, account_id=account.id, amount=amount_to_add)
    db.session.add(funding)
    db.session.commit()
    if goal.current_amount >= goal.target_amount:
        flash('Congratulations! You have reached your goal!')
    else:
        flash('Goal progress updated!')
    return redirect(url_for('goals')) 

@app.route('/delete_goal/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('goals'))
    if goal.current_amount > 0:
        fundings = GoalFunding.query.filter_by(goal_id=goal.id).all()
        total_funded = sum(f.amount for f in fundings)
        for funding in fundings:
            if total_funded > 0:
                refund_amount = (funding.amount / total_funded) * goal.current_amount
            else:
                refund_amount = 0
            account = Account.query.get(funding.account_id)
            if account:
                account.balance += refund_amount
                # Log a transaction
                transaction = Transaction(
                    amount=refund_amount,
                    description=f'Refund from deleted goal: {goal.name}',
                    category='Goal Refund',
                    transaction_type='income',
                    account_id=account.id
                )
                db.session.add(transaction)
        db.session.commit()
    GoalFunding.query.filter_by(goal_id=goal.id).delete()
    db.session.delete(goal)
    db.session.commit()
    flash('Goal deleted!')
    return redirect(url_for('goals'))

@app.route('/edit_goal_deadline/<int:goal_id>', methods=['POST'])
@login_required
def edit_goal_deadline(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('goals'))
    new_deadline_str = request.form.get('new_deadline')
    if not new_deadline_str:
        flash('No deadline provided.', 'error')
        return redirect(url_for('goals'))
    try:
        new_deadline = datetime.strptime(new_deadline_str, '%Y-%m-%d').date()
        goal.deadline = new_deadline
        db.session.commit()
        flash('Goal deadline updated!', 'success')
    except Exception:
        flash('Invalid date format.', 'error')
    return redirect(url_for('goals'))

@app.route('/analytics')
@login_required
def analytics():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    
    # Get all transactions for the user
    all_transactions = []
    for account in accounts:
        transactions = Transaction.query.filter_by(account_id=account.id).all()
        all_transactions.extend(transactions)
    
    # Calculate spending by category
    spending_by_category = {}
    income_by_category = {} 
    
    for transaction in all_transactions:
        if transaction.transaction_type == 'expense':
            if transaction.category in spending_by_category:
                spending_by_category[transaction.category] += transaction.amount
            else:
                spending_by_category[transaction.category] = transaction.amount
        else:
            if transaction.category in income_by_category:
                income_by_category[transaction.category] += transaction.amount
            else:
                income_by_category[transaction.category] = transaction.amount
    
    return render_template('analytics.html', 
                         spending_by_category=spending_by_category,
                         income_by_category=income_by_category)

# Expanded financial literacy tips grouped by category
financial_tips = {
    "Budgeting": [
        {"title": "How to Create a Budget", "content": "Track your income and expenses. Set spending limits for each category and review your budget monthly.", "video_url": "https://www.youtube.com/embed/r0HtVCOUbF0"},
        {"title": "50/30/20 Rule", "content": "Allocate 50% of your income to needs, 30% to wants, and 20% to savings or debt repayment.", "video_url": "https://www.youtube.com/embed/LKxOamnP8J4"},
        {"title": "Review Regularly", "content": "Check your budget at least once a month and adjust as needed."},
        {"title": "Zero-Based Budgeting", "content": "Assign every dollar a job so your income minus expenses equals zero."},
        {"title": "Track Your Spending", "content": "Use apps or spreadsheets to monitor where your money goes."},
        {"title": "Distinguish Needs vs Wants", "content": "Prioritize essentials and limit discretionary spending."},
        {"title": "Emergency Fund in Budget", "content": "Include savings for emergencies as a budget category."},
    ],
    "Credit": [
        {"title": "Understanding Credit Scores", "content": "Your credit score affects your ability to borrow money. Pay bills on time and keep credit card balances low.", "video_url": "https://www.youtube.com/embed/c0TQlgoUHRE"},
        {"title": "How to Build Credit", "content": "Use credit responsibly, pay your bills on time, and avoid maxing out your cards."},
        {"title": "Check Your Credit Report", "content": "Review your credit report annually for errors and dispute any inaccuracies."},
        {"title": "Credit Utilization", "content": "Keep your credit card balances below 30% of your limit."},
        {"title": "Avoid Hard Inquiries", "content": "Too many credit applications in a short time can lower your score."},
        {"title": "Length of Credit History", "content": "The longer your credit accounts are open, the better for your score."},
    ],
    "Investing": [
        {"title": "Investing 101", "content": "Start investing early, diversify your portfolio, and focus on long-term growth.", "video_url": "https://www.youtube.com/embed/dwCJnIelhdY"},
        {"title": "Compound Interest", "content": "Earnings on your investments generate their own earnings. The earlier you start, the more you benefit."},
        {"title": "Diversification", "content": "Spread your investments across different asset types to reduce risk."},
        {"title": "Risk vs Reward", "content": "Higher returns usually come with higher risk. Know your risk tolerance."},
        {"title": "Long-Term vs Short-Term", "content": "Investing for the long term can help ride out market ups and downs."},
        {"title": "Index Funds", "content": "Index funds offer broad market exposure and low fees."},
    ],
    "Saving": [
        {"title": "Emergency Fund Basics", "content": "Aim to save at least 3-6 months of living expenses in an easily accessible account.", "video_url": "https://www.youtube.com/embed/8w_u4Y-m-JY"},
        {"title": "Automate Savings", "content": "Set up automatic transfers to your savings account to make saving effortless."},
        {"title": "Set Clear Goals", "content": "Define what you're saving for and set a timeline to stay motivated."},
        {"title": "High-Interest Savings Accounts", "content": "Look for accounts with higher interest rates to grow your savings faster."},
        {"title": "Save Windfalls", "content": "Put bonuses, tax refunds, or gifts into savings instead of spending them."},
        {"title": "Pay Yourself First", "content": "Treat savings like a non-negotiable expense in your budget."},
    ],
    "Banking Basics": [
        {"title": "Types of Bank Accounts", "content": "Understand the differences between checking, savings, and investment accounts.", "video_url": "https://www.youtube.com/embed/E-HOz8T6tAo"},
        {"title": "How to Avoid Fees", "content": "Maintain minimum balances and use in-network ATMs to avoid unnecessary fees."},
        {"title": "Online Banking Safety", "content": "Use strong passwords and enable two-factor authentication for your accounts."},
        {"title": "FDIC Insurance", "content": "Ensure your bank is FDIC insured to protect your deposits."},
        {"title": "Direct Deposit", "content": "Set up direct deposit for faster and safer access to your paycheck."},
        {"title": "Reconciling Statements", "content": "Regularly check your bank statements for errors or fraud."},
    ],
    "Taxes": [
        {"title": "What Are Taxes?", "content": "Taxes are mandatory payments to the government, used to fund public services and infrastructure.", "video_url": "https://www.youtube.com/embed/OGVJfcSckUs"},
        {"title": "Types of Taxes", "content": "Common types include income tax, sales tax, property tax, and payroll tax."},
        {"title": "Filing a Tax Return", "content": "Most people must file a tax return each year to report income and calculate taxes owed or refunds."},
        {"title": "Tax Deductions", "content": "Deductions reduce your taxable income. Examples: student loan interest, mortgage interest, and charitable donations."},
        {"title": "Tax Credits", "content": "Credits directly reduce your tax bill. Examples: Earned Income Tax Credit, Child Tax Credit."},
        {"title": "Withholding", "content": "Employers withhold taxes from your paycheck and send them to the government on your behalf."},
        {"title": "Did you know?", "content": "Filing electronically and choosing direct deposit is the fastest way to get your tax refund."},
        {"title": "Keep Records", "content": "Keep tax documents for at least 3 years in case of an audit."},
        {"title": "Tax Brackets", "content": "The U.S. uses a progressive tax system—higher income is taxed at higher rates."},
        {"title": "Filing Status", "content": "Your filing status (single, married, head of household) affects your tax rate and deductions."},
    ],
}

@app.route('/learn')
def learn():
    return render_template('learn.html', tips=financial_tips)

# Multi-topic quizzes with explanations
quizzes = {
    "Budgeting": [
        {"question": "According to the video, what is the first step in creating a budget?", "options": ["Track your income and expenses", "Apply for a loan", "Buy a new phone"], "answer": 0, "explanation": "The video and tip both emphasize tracking your income and expenses as the first step."},
        {"question": "What does the 50/30/20 rule recommend you do with your income?", "options": ["Spend it all on wants", "Allocate 50% to needs, 30% to wants, 20% to savings/debt", "Save 100%"], "answer": 1, "explanation": "The 50/30/20 rule is a budgeting method: 50% needs, 30% wants, 20% savings/debt."},
        {"question": "Why should you review your budget regularly?", "options": ["To adjust for changes in income/expenses", "To increase spending", "To avoid saving"], "answer": 0, "explanation": "Regular reviews help you stay on track and adjust as needed."},
        {"question": "What is zero-based budgeting?", "options": ["A budget with zero expenses", "A budget for zero income", "A budget where every dollar is assigned a job"], "answer": 2, "explanation": "Zero-based budgeting means every dollar is assigned a purpose."},
        {"question": "Why is it important to distinguish needs from wants?", "options": ["To prioritize essentials and limit discretionary spending", "To spend more on wants", "To ignore savings"], "answer": 0, "explanation": "Distinguishing needs from wants helps you prioritize essentials and control spending."},
    ],
    "Credit": [
        {"question": "According to the video, what is the biggest factor affecting your credit score?", "options": ["Paying bills on time", "Number of bank accounts", "Your job title"], "answer": 0, "explanation": "Payment history is the biggest factor in your credit score."},
        {"question": "What is credit utilization?", "options": ["The amount of credit you use compared to your limit", "Your credit score", "The number of credit cards you have"], "answer": 0, "explanation": "Credit utilization is the ratio of your credit card balances to your limits."},
        {"question": "How can you build credit?", "options": ["Pay bills late", "Use credit responsibly and pay on time", "Max out your cards"], "answer": 1, "explanation": "Using credit responsibly and paying bills on time builds credit."},
        {"question": "Why should you check your credit report annually?", "options": ["To review for errors and dispute inaccuracies", "To increase your score automatically", "To close your accounts"], "answer": 0, "explanation": "Reviewing your credit report helps you spot and fix errors."},
    ],
    "Investing": [
        {"question": "According to the video, why is it important to start investing early?", "options": ["To benefit from compound interest", "To avoid taxes", "To get rich quick"], "answer": 0, "explanation": "Starting early lets you benefit from compound interest and long-term growth."},
        {"question": "What is diversification?", "options": ["Investing in one stock", "Spreading investments across assets", "Only buying bonds"], "answer": 1, "explanation": "Diversification reduces risk by spreading investments."},
        {"question": "What is an index fund?", "options": ["A single company stock", "A fund that tracks a market index", "A type of loan"], "answer": 1, "explanation": "Index funds track a market index and offer diversification."},
    ],
    "Saving": [
        {"question": "According to the video, what is an emergency fund?", "options": ["Money for vacations", "Savings for unexpected expenses", "Investment in stocks"], "answer": 1, "explanation": "An emergency fund is for unexpected expenses like job loss or medical bills."},
        {"question": "How can you make saving easier?", "options": ["Automate transfers", "Spend more", "Ignore your savings"], "answer": 0, "explanation": "Automating savings helps you save consistently."},
        {"question": "What is a high-interest savings account?", "options": ["An account with a high interest rate", "A checking account", "A loan account"], "answer": 0, "explanation": "High-interest savings accounts help your money grow faster."},
    ],
    "Banking Basics": [
        {"question": "According to the video, what is the main function of a checking account?", "options": ["Daily transactions", "Long-term investing", "Building credit"], "answer": 0, "explanation": "Checking accounts are for everyday spending and bill payments."},
        {"question": "How can you avoid bank fees?", "options": ["Maintain minimum balances and use in-network ATMs", "Withdraw cash frequently", "Ignore account statements"], "answer": 0, "explanation": "Maintaining minimum balances and using in-network ATMs helps avoid fees."},
        {"question": "What is FDIC insurance?", "options": ["A type of investment", "Insurance for bank deposits", "A loan"], "answer": 1, "explanation": "FDIC insurance protects your deposits if the bank fails."},
    ],
    "Taxes": [
        {"question": "According to the video, what are taxes used for?", "options": ["Funding public services", "Personal savings", "Company profits"], "answer": 0, "explanation": "Taxes fund public services like roads, schools, and safety."},
        {"question": "What is a tax deduction?", "options": ["A reduction in taxable income", "A penalty", "A tax increase"], "answer": 0, "explanation": "Deductions reduce your taxable income."},
        {"question": "What is a tax credit?", "options": ["A direct reduction of your tax bill", "A loan", "A tax penalty"], "answer": 0, "explanation": "Credits directly reduce the amount of tax you owe."},
    ],
}

@app.route('/quiz')
def quiz_select():
    return render_template('quiz_select.html', topics=quizzes.keys())

@app.route('/quiz/<topic>', methods=['GET', 'POST'])
def quiz(topic):
    all_questions = quizzes.get(topic, [])
    num_questions = min(5, len(all_questions))  # Show 5 random questions per quiz
    if request.method == 'GET':
        questions = random.sample(all_questions, num_questions)
        session['quiz_questions'] = questions
    else:
        questions = session.get('quiz_questions', all_questions[:num_questions])
    user_answers = []
    score = None
    explanations = []
    if request.method == 'POST':
        for i in range(len(questions)):
            user_answer = request.form.get(f'q{i}')
            user_answers.append(int(user_answer) if user_answer is not None else None)
        score = sum(1 for i, q in enumerate(questions) if user_answers[i] == q['answer'])
        explanations = [q['explanation'] for i, q in enumerate(questions)]
    return render_template('quiz.html', questions=questions, user_answers=user_answers, score=score, topic=topic, explanations=explanations)

@app.route('/transactions/<int:account_id>/export')
@login_required
def export_transactions(account_id):
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('transactions', account_id=account_id))
    transactions = Transaction.query.filter_by(account_id=account_id).order_by(Transaction.date.desc()).all()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Date', 'Description', 'category', 'Amount', 'Type'])
    for t in transactions:
        cw.writerow([
            t.date.strftime('%Y-%m-%d %H:%M') if t.date else '',
            t.description,
            t.category,
            f'{t.amount:.2f}',
            t.transaction_type.capitalize()
        ])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=transactions_{account_id}.csv"}
    )

@app.route('/transactions/export/all')
@login_required
def export_all_transactions():
    accounts = Account.query.filter_by(user_id=current_user.id).all()
    account_map = {a.id: a for a in accounts}
    transactions = []
    for account in accounts:
        transactions.extend(Transaction.query.filter_by(account_id=account.id).all())
    transactions.sort(key=lambda t: t.date, reverse=True)
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Date', 'Description', 'Category', 'Amount', 'Type', 'Account'])
    for t in transactions:
        account = account_map.get(t.account_id)
        account_str = f'{account.name} ({account.account_type})' if account else ''
        cw.writerow([
            t.date.strftime('%Y-%m-%d %H:%M') if t.date else '',
            t.description,
            t.category,
            f'{t.amount:.2f}',
            t.transaction_type.capitalize(),
            account_str
        ])
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=all_transactions.csv"}
    )

@app.route('/withdraw_goal/<int:goal_id>', methods=['POST'])
@login_required
def withdraw_goal(goal_id):
    goal = Goal.query.get_or_404(goal_id)
    if goal.user_id != current_user.id:
        flash('Access denied', 'error')
        return redirect(url_for('goals'))
    try:
        amount = float(request.form['withdraw_amount'])
        account_id = int(request.form['account_id'])
    except (KeyError, ValueError):
        flash('Invalid input.', 'error')
        return redirect(url_for('goals'))
    account = Account.query.get_or_404(account_id)
    if account.user_id != current_user.id:
        flash('Invalid account selected', 'error')
        return redirect(url_for('goals'))
    if amount <= 0:
        flash('Amount must be positive', 'error')
        return redirect(url_for('goals'))
    if goal.current_amount < amount:
        flash('Insufficient funds in goal', 'error')
        return redirect(url_for('goals'))
    # Transfer funds
    goal.current_amount -= amount
    account.balance += amount
    # Log as a transaction
    transaction = Transaction(
        amount=amount,
        description=f'Withdrawn from goal: {goal.name}',
        category='Goal Withdrawal',
        transaction_type='income',
        account_id=account.id
    )
    db.session.add(transaction)
    db.session.commit()
    flash('Funds withdrawn from goal and added to account!', 'success')
    return redirect(url_for('goals'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True) 