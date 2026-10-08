# SmartBank - Your Financial Companion

A modern, creative bank website where users can track their finances, set savings goals, and achieve financial freedom through intelligent financial management.

## 🚀 Features

### 💰 Financial Management
- **Multi-Account Support**: Manage checking, savings, credit, and investment accounts
- **Transaction Tracking**: Record income and expenses with detailed categorization
- **Real-time Balance Updates**: Automatic balance calculations across all accounts
- **Transaction History**: Complete history with search and filtering capabilities

### 🎯 Goal Setting & Tracking
- **Financial Goals**: Set savings targets with deadlines and categories
- **Progress Visualization**: Visual progress bars and percentage tracking
- **Goal Categories**: Emergency fund, vacation, home, car, education, and more
- **Milestone Celebrations**: Track progress towards financial freedom

### 📊 Smart Analytics
- **Spending Analysis**: Visual breakdown of expenses by category
- **Income Tracking**: Monitor income sources and patterns
- **Interactive Charts**: Beautiful doughnut charts using Chart.js
- **Financial Health Metrics**: Net savings calculations and insights

### 🔐 Security & User Experience
- **User Authentication**: Secure login and registration system
- **Password Protection**: Encrypted password storage
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Modern UI/UX**: Beautiful gradients, animations, and intuitive navigation

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Custom CSS with gradients and animations
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome
- **Fonts**: Google Fonts (Poppins)

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd PythonProject
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional)**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your-secret-key-here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## 🎨 Features Overview

### Landing Page
- Attractive hero section with animated floating cards
- Feature showcase with modern design
- Call-to-action sections for user engagement

### Dashboard
- **Overview Cards**: Total balance, account count, active goals
- **Account Summary**: Quick view of all accounts with balances
- **Goal Progress**: Visual progress tracking for financial goals
- **Recent Transactions**: Latest financial activity

### Account Management
- **Add New Accounts**: Create checking, savings, credit, or investment accounts
- **Account Overview**: View balances and account types
- **Transaction History**: Detailed transaction logs with categorization

### Transaction Tracking
- **Add Transactions**: Record income and expenses
- **Category System**: Food, transportation, shopping, entertainment, etc.
- **Transaction Types**: Income vs expense tracking
- **Real-time Updates**: Instant balance updates

### Goal Setting
- **Create Goals**: Set financial targets with deadlines
- **Progress Tracking**: Visual progress bars and percentage completion
- **Category Support**: Emergency fund, vacation, home, car, etc.
- **Update Progress**: Add amounts to track goal advancement

### Analytics
- **Spending Charts**: Visual breakdown of expenses by category
- **Income Analysis**: Track income sources and patterns
- **Financial Summary**: Total spending, income, and net savings
- **Interactive Visualizations**: Beautiful charts and graphs

## 🎯 Key Features for Financial Management

### Expense Tracking
- Categorize expenses (Food & Dining, Transportation, Shopping, etc.)
- Track spending patterns over time
- Identify areas for potential savings

### Income Management
- Record different income sources
- Track salary, investments, and other income
- Monitor income trends

### Savings Goals
- Set realistic financial targets
- Track progress with visual indicators
- Stay motivated with milestone tracking

### Financial Insights
- Understand spending habits
- Identify saving opportunities
- Monitor financial health

## 🔧 Customization

### Adding New Categories
Edit the transaction forms in `templates/transactions.html` and `templates/goals.html` to add new categories.

### Styling Changes
Modify `static/css/style.css` to customize colors, fonts, and layout.

### Database Schema
The application uses SQLAlchemy models in `app.py`. Modify the models to add new fields or relationships.

## 🚀 Deployment

### Local Development
The application runs on Flask's development server by default. For production deployment:

1. **Set up a production WSGI server** (Gunicorn, uWSGI)
2. **Configure environment variables**
3. **Set up a production database** (PostgreSQL, MySQL)
4. **Configure reverse proxy** (Nginx, Apache)

### Environment Variables
- `SECRET_KEY`: Flask secret key for session management
- `DATABASE_URL`: Database connection string (for production)

## 📱 Mobile Responsiveness

The application is fully responsive and works great on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🔒 Security Features

- Password hashing with bcrypt
- Session management with Flask-Login
- CSRF protection
- Input validation and sanitization
- Secure authentication system

## 🎨 Design Features

- **Modern Gradient Design**: Beautiful purple-blue gradients
- **Glass Morphism**: Translucent cards with backdrop blur
- **Smooth Animations**: Hover effects and transitions
- **Responsive Layout**: Adapts to all screen sizes
- **Interactive Elements**: Hover states and feedback

## 📈 Future Enhancements

Potential features for future versions:
- Budget planning and tracking
- Bill reminders and notifications
- Investment portfolio tracking
- Export functionality (PDF, CSV)
- Multi-currency support
- Financial reports and insights
- Mobile app development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the documentation
2. Review the code comments
3. Create an issue in the repository

---

**SmartBank** - Empowering users to take control of their financial future with intelligent tracking and goal-setting tools. 