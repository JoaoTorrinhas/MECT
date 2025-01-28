package ex2;

public class Stack {
    //storage array
    private int[] stack;

    //stack pointer
    private int ptr;

    //size of the stack
    private int size;

    //id of the stack
    private char id;

    public Stack(int size, char id) {
        this.size = size;
        this.stack = new int[size];
        this.ptr = 0;
        this.id = id;
    }

    public boolean isEmpty() {
        return ptr == 0;
    }

    public boolean isFull() {
        return ptr == size;
    }

    public void push(int c) {
        if(isFull()) {
            System.out.println("ERROR: Stack is full");
            return;
        }
        stack[ptr] = c;
        ptr++;
    }

    public int pop() {
        if(isEmpty()) {
            System.out.println("ERROR: Stack is empty");
            return 0;
        }
        ptr--;
        return stack[ptr];
    }

    public int peek() {
        if(isEmpty())
            return 0;
        return stack[ptr-1];
    }

    public char getId() {
        return this.id;
    }

    @Override
    public String toString() {
        String s="[";
        for(int i=0; i < size; i++) {
            if(i < ptr)
                s = s + stack[i];
            else
                s = s +"-";
            if(i != size-1)
                s = s +" ";
        }
        return s+"]";
    }


}