class ControlFlow {
    public void checkNumber(int num) {
        if (num > 0) {
            System.out.println("Positive");
        } else if (num < 0) {
            System.out.println("Negative");
        } else {
            System.out.println("Zero");
        }
    }
    
    public boolean isEven(int number) {
        if (number % 2 == 0) {
            return true;
        } else {
            return false;
        }
    }

    public static void main(String[] args) {
        ControlFlow cf = new ControlFlow();
        cf.checkNumber(5);
        cf.checkNumber(-2);
        cf.checkNumber(0);
        System.out.println("Even: " + cf.isEven(4));
        System.out.println("Even: " + cf.isEven(7));
    }
}
