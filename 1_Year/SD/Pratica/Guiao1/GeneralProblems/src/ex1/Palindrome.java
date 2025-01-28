package ex1;
import java.util.*;

public class Palindrome {
    public static void main(String[] args) {
        //read a string
        Scanner sc = new Scanner(System.in);
        System.out.println("Insert a string:");
        String str = sc.nextLine(); //read string

        int size = str.length();
        FIFO fifo = new FIFO(size);
        Stack stack = new Stack(size);

        //Insert chars into the stack and fifo
        for (int i = 0; i < size; i++){
            //System.out.println(str.charAt(i));
            fifo.push(str.charAt(i));
            stack.push(str.charAt(i));
        }
        //System.out.println(fifo.toString());
        //System.out.println(stack.toString());

        //Check if all characteres are the same
        while(!fifo.isEmpty()) {
            if(fifo.pop() != stack.pop()) {
                System.out.println("String is not a palindrome!");
                System.exit(0);
            }
        }
        System.out.println("String is a palindrome!");
    }
}
