class BankAccount {
    public String accountHolder = "John Doe";
    public double balance = 1000.0;
    
    public void deposit(double amount) {
        if (amount > 0) {
            balance = balance + amount;
            System.out.println("Deposit successful");
        } else {
            System.out.println("Invalid amount");
        }
    }
    
    public boolean withdraw(double amount) {
        if (amount <= balance) {
            balance = balance - amount;
            return true;
        } else {
            return false;
        }
    }
    
    public double getBalance() {
        return balance;
    }

    public static void main(String[] args) {
        BankAccount account = new BankAccount();
        account.deposit(500.0);
        System.out.println("Balance: " + account.getBalance());
        System.out.println("Withdraw ok: " + account.withdraw(200.0));
        System.out.println("Balance: " + account.getBalance());
    }
}
