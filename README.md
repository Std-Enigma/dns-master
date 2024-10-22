# 🚀 DNS Master

DNS Master is a command-line tool designed to simplify the management of your DNS configurations 🌐. It allows you to easily add, modify, delete, and copy DNS settings right from your terminal. DNS configurations are stored in an SQLite database 🗄️, ensuring persistent storage. The application is built using Python 🐍, Typer for the CLI interface, and Rich for enhanced terminal output ✨.

## 🎯 Features

- **📝 Add DNS Configurations:** Create and save DNS configurations with unique identifiers.
- **🛠️ Modify Configurations:** Update existing configurations by changing DNS addresses or identifiers.
- **🗑️ Remove Configurations:** Delete any DNS configuration or clear all at once.
- **📜 List Configurations:** View all saved configurations or filter by specific identifiers.
- **📋 Copy to Clipboard:** Quickly copy primary, secondary, or both DNS addresses to your clipboard for easy use.

## 🛠️ Technologies

- 🐍 **Python**
- 🗄️ **SQLite** for database management
- ⌨️ **Typer** for command-line interactions
- 🎨 **Rich** for enhanced terminal output and styling

## 📦 Installation

To install and set up DNS Master:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/dns-master.git
   cd dns-master
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### ➕ Add a DNS Configuration

```bash
dns-master add <identifier> <primary-dns> [secondary-dns] [description]
```

Example:

```bash
dns-master add google 8.8.8.8 8.8.4.4 "Google's DNS"
```

### 📜 List All Configurations

```bash
dns-master list
```

### 📋 Copy DNS Address to Clipboard

```bash
dns-master copy <identifier>
```

You will be prompted to select whether to copy the primary, secondary, or both addresses.

### 🛠️ Modify a DNS Configuration

```bash
dns-master modify <identifier> [new_identifier] [new_primary_dns] [new_secondary_dns] [new_description]
```

### 🗑️ Remove a DNS Configuration

```bash
dns-master remove <identifier> [--force]
```

To skip confirmation, use the `--force` option.

### 🚮 Clear All Configurations

```bash
dns-master clear [--force]
```

Use the `--force` option to delete all configurations without confirmation.

## 📜 License

This project is licensed under the **GPL license**. See the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please submit issues and pull requests to improve the tool.
