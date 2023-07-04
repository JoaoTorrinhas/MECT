package ex1;
import java.util.Arrays;

public class Stack {
    private char[] stack; //storage array
    private int ptr; // pointer
    private int size; //size of the stack

    //Constructor
    public Stack(int size) {
        this.size = size;
        this.stack = new char[size];
        this.ptr = 0;
    }

    //c character to be inserted at the top of the stack
    public void push(char c) {
        if(ptr == size) {
            System.out.println("ERROR: Stack is full");
            return;
        }
        System.out.println("Inserting " + c);
        stack[ptr] = c;
        ptr++;
    }

    //character at the top of the stack
    public char pop() {
        if(ptr == 0) {
            System.out.println("ERROR: Stack is empty");
            return 0;
        }
        ptr--;
        return stack[ptr];
    }

    @Override
    public String toString() {
        return "Stack [stack=" + Arrays.toString(stack) + "]";
    }
}
