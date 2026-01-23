class Loops {
    public int sumNumbers(int n) {
        int sum = 0;
        int i = 1;
        while (i <= n) {
            sum = sum + i;
            i = i + 1;
        }
        return sum;
    }
    
    public int factorial(int n) {
        int result = 1;
        for (int i = 2; i <= n; i++) {
            result = result * i;
        }
        return result;
    }

    public static void main(String[] args) {
        Loops loops = new Loops();
        System.out.println(loops.sumNumbers(10));
        System.out.println(loops.factorial(5));
    }
}
