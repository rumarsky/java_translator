class ArrayDemo {
    public String first(String[] items) {
        return items[0];
    }

    public int sumFirstTwo(int[] nums) {
        return nums[0] + nums[1];
    }

    public static void main(String[] args) {
        ArrayDemo demo = new ArrayDemo();
        if (args != null && args.length > 0) {
            System.out.println(demo.first(args));
        } else {
            System.out.println("No args");
        }
    }
}
