# Budget Manager 💰

[![CI Pipeline](https://github.com/MelyRz-Official/BudgetEX/actions/workflows/ci.yml/badge.svg)](https://github.com/MelyRz-Official/BudgetEX/actions/workflows/ci.yml)
[![Code Quality](https://github.com/MelyRz-Official/BudgetEX/actions/workflows/code-quality.yml/badge.svg)](https://github.com/MelyRz-Official/BudgetEX/actions/workflows/code-quality.yml)
[![Release](https://github.com/MelyRz-Official/BudgetEX/actions/workflows/release.yml/badge.svg)](https://github.com/MelyRz-Official/BudgetEX/actions/workflows/release.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> A professional personal finance management application built with modern software architecture and comprehensive testing. Features intelligent budget tracking, multiple scenario planning, and real-time financial calculations with a beautiful dark theme interface.

## ✨ Features

### 🎯 **Smart Budget Management**
- **Multiple Budget Scenarios**: July-December 2025, Fresh New Year planning periods
- **Fixed vs. Percentage Categories**: Intelligent handling of fixed expenses (rent, utilities) vs. percentage-based allocations
- **Real-time Calculations**: Live budget updates with over/under spending indicators
- **Automatic Backup**: SQLite database with automated backup functionality

### 🎨 **Modern User Interface**
- **Dark Theme**: Professional Sun Valley theme with modern aesthetics
- **Intuitive Design**: Clean, organized layout with color-coded status indicators
- **Interactive Charts**: Real-time pie charts and bar graphs for budget visualization
- **Responsive Layout**: Optimized for various screen sizes and resolutions

### 🏗️ **Professional Architecture**
- **MVC Pattern**: Clean separation of Model, View, and Controller layers
- **Configuration Management**: Centralized settings with user customization
- **Comprehensive Testing**: Unit, integration, and performance tests
- **Type Safety**: Full type hints and static analysis support

### 🔒 **Enterprise-Grade Quality**
- **CI/CD Pipeline**: Automated testing across multiple Python versions and platforms
- **Security Scanning**: Automated vulnerability detection and dependency monitoring
- **Code Quality**: Enforced formatting, linting, and type checking
- **Cross-Platform**: Native support for Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- Git (for development)

### Installation

#### Option 1: Download Release (Recommended)
1. Go to [Releases](https://github.com/MelyRz-Official/BudgetEX/releases)
2. Download the latest release for your operating system
3. Extract and run the executable

#### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/MelyRz-Official/BudgetEX.git
cd BudgetEX

# Install dependencies
pip install -r requirements.txt

# Run the application
python budget_app.py
```

#### Option 3: Development Setup
```bash
# Clone and setup development environment
git clone https://github.com/MelyRz-Official/BudgetEX.git
cd BudgetEX

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
python run_tests.py
```

## 📖 Usage

### Getting Started
1. **Launch the Application**: Run `python budget_app.py`
2. **Select Budget Scenario**: Choose from predefined scenarios or customize your own
3. **Set Paycheck Amount**: Enter your income amount for automatic calculations
4. **Track Spending**: Input actual expenses in each category
5. **Monitor Progress**: View real-time charts and budget status

### Budget Scenarios

#### July-December 2025 (Current)
Optimized for current year budgeting with balanced allocations:
- Fixed expenses: HOA ($1,078.81), Utilities ($60), Subscriptions ($90), Therapy ($44)
- Percentage-based: Roth IRA (8.4%), General Savings (19.3%), Vacation Fund (12.5%)

#### Fresh New Year (Jan-May)
High retirement contribution strategy:
- Maximized Roth IRA contributions (35.2% to hit annual limit early)
- Reduced discretionary spending for aggressive saving

#### Fresh New Year (June-Dec)
Post-retirement contribution strategy:
- Roth IRA maxed out (0% allocation)
- Increased general savings (20.9%) and vacation fund (7.5%)

### Key Features

#### Smart Category Management
- **Fixed Amount Categories**: Automatically maintain dollar amounts regardless of income changes
- **Percentage Categories**: Scale with income for flexible budgeting
- **Status Indicators**: Color-coded feedback (Green=Under Budget, Red=Over Budget)

#### Data Management
- **Auto-Save**: Optional automatic saving of changes
- **Manual Save**: Explicit control over data persistence
- **Export Options**: CSV export for external analysis
- **Backup System**: Automated database backups with configurable frequency

#### Customization
- **Themes**: Light and dark mode support
- **Currency**: Configurable currency symbol and decimal places
- **Notifications**: Customizable budget alerts and status updates

## 🛠️ Development

### Architecture Overview

```
Budget Manager/
├── models/                 # Business logic and data management
│   ├── budget_model.py    # Core budget calculations and scenarios
│   └── database_manager.py # SQLite database operations
├── controllers/           # Application flow control
│   └── budget_controller.py # Coordinates between model and views
├── views/                 # User interface components (future expansion)
├── tests/                 # Comprehensive test suite
│   ├── unit/             # Unit tests for individual components
│   ├── integration/      # Integration tests for workflows
│   └── performance/      # Performance and load tests
├── config.py             # Configuration management
└── budget_app.py         # Main application entry point
```

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run with pytest for detailed output
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=models --cov=controllers --cov=config --cov-report=html

# Run performance tests
pytest tests/ -m performance
```

### Code Quality

This project maintains high code quality standards:

```bash
# Format code
black models/ controllers/ config.py *.py

# Sort imports
isort models/ controllers/ config.py *.py

# Lint code
flake8 models/ controllers/ config.py --max-line-length=100

# Type checking
mypy models/ controllers/ config.py --ignore-missing-imports

# Security scanning
bandit -r models/ controllers/ config.py
```

### Contributing

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/your-feature-name`
3. **Write Tests**: Ensure new functionality is tested
4. **Follow Code Style**: Run formatting and linting tools
5. **Update Documentation**: Update README and docstrings as needed
6. **Submit Pull Request**: Include description of changes and test results

## 📊 Technical Specifications

### Performance
- **Startup Time**: < 2 seconds on modern hardware
- **Memory Usage**: ~50MB RAM for typical usage
- **Database Size**: ~1MB for years of budget data
- **Response Time**: < 100ms for all budget calculations

### Compatibility
- **Python Versions**: 3.9, 3.10, 3.11, 3.12
- **Operating Systems**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Dependencies**: Minimal external dependencies for easy deployment

### Security
- **Data Privacy**: All financial data stored locally
- **No Network Access**: No data transmitted to external servers
- **Secure Storage**: SQLite database with proper access controls
- **Dependency Scanning**: Automated vulnerability monitoring

## 🎯 Roadmap

### Version 1.1 (Planned)
- [ ] Advanced reporting with charts and trends
- [ ] Budget goal tracking and notifications
- [ ] Import from CSV/Excel files
- [ ] Multi-currency support

### Version 1.2 (Future)
- [ ] Mobile companion app
- [ ] Cloud sync capabilities (optional)
- [ ] Machine learning spending predictions
- [ ] Advanced analytics dashboard

### Version 2.0 (Vision)
- [ ] Web-based interface
- [ ] API for third-party integrations
- [ ] Advanced financial planning tools
- [ ] Investment tracking integration

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Acknowledgments

- **Sun Valley Theme**: Modern tkinter theme by [@rdbende](https://github.com/rdbende/Sun-Valley-ttk-theme)
- **Matplotlib**: Powerful plotting library for data visualization
- **Python Community**: For excellent testing and development tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MelyRz-Official/BudgetEX/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MelyRz-Official/BudgetEX/discussions)
- **Documentation**: [Project Wiki](https://github.com/MelyRz-Official/BudgetEX/wiki)

## 🔧 Troubleshooting

### Common Issues

**Application won't start**
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Theme not loading**
```bash
# Install theme package
pip install sv-ttk

# Verify installation
python -c "import sv_ttk; print('Theme available')"
```

**Database errors**
```bash
# Reset database (warning: deletes all data)
rm budget_data.db

# Run application to recreate database
python budget_app.py
```

**Import errors**
```bash
# Verify project structure
python -c "import config; print('Config OK')"
python -c "from models.budget_model import BudgetModel; print('Model OK')"
```

---

<div align="center">

**[⭐ Star this repository](https://github.com/MelyRz-Official/BudgetEX)** if you find it useful!

Made with ❤️ by [Melissa Ruiz](https://github.com/MelyRz-Official)

</div>