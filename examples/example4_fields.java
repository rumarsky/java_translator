class Person {
    public String name = "John";
    public int age = 30;
    
    public void displayInfo() {
        System.out.println(name);
        System.out.println(age);
    }
    
    public void setAge(int newAge) {
        age = newAge;
    }
    
    public int getAge() {
        return age;
    }
}
