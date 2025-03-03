# Control Host Environment Setup Guide

This document provides detailed instructions to set up the environment on the control host. Follow the steps carefully to ensure all necessary dependencies are installed correctly.

## 1. Install Anaconda

To begin, you need to install Anaconda, a widely-used package manager and environment management system for Python.

### Step 1: Download Anaconda
1. Go to the [official Anaconda website](https://www.anaconda.com/products/individual) and download the installer for your operating system.
2. Choose the version that matches your system architecture.
   - For most users, the Python 3.x version is recommended.

### Step 2: Install Anaconda
1. Once the `.exe` installer has been downloaded, double-click to run it. 
2.  During the installation process, make sure to check the option "Add Anaconda to my PATH environment variable" for ease of access to Anaconda through the command line. 
3. Follow the installation instructions to complete the process.

### Step 3: Verify Installation

After installation, you need to verify that Anaconda has been successfully installed on your system.

#### How to Open Anaconda Prompt
1. **Click the Start Menu** (bottom-left corner of your screen).
2. Type `Anaconda Prompt` in the search bar.
3. Click on the **Anaconda Prompt** application to open it.

Alternatively, you can use **Command Prompt**:
1. Press `Win + R` to open the Run dialog.
2. Type `cmd` and press **Enter** to open Command Prompt.

Once you have the terminal open, check if Anaconda was successfully installed by typing the following command:
```bash
conda --version
```



## 2. Activate Anaconda Environment

Once Anaconda is installed, you need to create and activate the virtual environment for your project.

### Step 1: Create a New Environment

You can create a new environment by specifying the name and Python version. Run the following command in the terminal:

```
conda create --name <environment_name> python=3.7
```

Replace `<environment_name>` with your desired environment name, and choose the appropriate Python version.

### Step 2: Activate the Environment

To activate the newly created environment, use the following command:

```
conda activate <environment_name>
```

You should now see the environment name in your terminal prompt, indicating the environment is active.



## 3. Install Dependencies from `requirements.txt`

The next step is to install the necessary Python packages for your project. These packages are listed in the `requirements.txt` file.

### Step 1: Ensure `pip` is Installed

If `pip` is not installed, you can install it using the following command:

```
conda install pip
```

### Step 2: Install the Packages

With the environment activated, navigate to the directory where your `requirements.txt` file is located and run the following command:

```
pip install -r requirements.txt
```

This will install all the dependencies listed in the `requirements.txt` file.

### Step 3: Verify Package Installation

To verify that all packages have been installed correctly, you can list the installed packages with:

```
pip list
```

