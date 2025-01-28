package ex1;
import java.util.Arrays;
public class FIFO {
    private char[] fifo;
    private int ptIn, ptOut;
    private int size;

    //Construtor
    public FIFO(int size) {
        this.size = size;
        this.fifo = new char[size];
        this.ptIn = 0;
        this.ptOut = 0;
    }

    public boolean isEmpty(){
        return ptIn == ptOut;
    }
    public void push(char c){
        if ((ptIn % size) == size){
            System.out.println("\nFIFO is full!\n");
            return;
        }
        else{
            fifo[ptIn % size] = c;
            ptIn++;
        }
    }

    public char pop() {
        if(ptIn == ptOut) {
            System.out.println("\nFIFO is empty\n");
            return 0;
        }
        int i = ptOut;
        ptOut++;
        return fifo[i % size];

    }

    @Override
    public String toString() {
        return "Fifo [fifo=" + Arrays.toString(fifo) + "]";
    }


}
