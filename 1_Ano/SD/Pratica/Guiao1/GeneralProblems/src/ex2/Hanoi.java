package ex2;

public class Hanoi {
    public static void main(String[] args) {
        HanoiTowers t = new HanoiTowers(9);
        System.out.println(t.toString());
        t.resolv();
        System.out.println();
        System.out.println(t.toString());
    }
}
