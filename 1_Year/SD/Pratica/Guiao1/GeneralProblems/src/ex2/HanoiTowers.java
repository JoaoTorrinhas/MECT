package ex2;

public class HanoiTowers {
    //Array of towers (3 towers)
    private Stack [] towers;

    //Number of disks
    private int nDisks;


    public HanoiTowers(int n) {
        this.nDisks = n;
        this.towers = new Stack[3];
        char aux = 'A';

        //Initialize towers
        for(int i=0; i < 3; i++) {
            towers[i] = new Stack(n, aux);
            aux++;
        }

        //Insert disks in the first tower
        for(int i = n; i > 0; i--) {
            towers[0].push(i);
        }
    }


    //Move disk from one tower to another
    //towerOrigin Origin tower
    //towerDestiny Destiny tower
    public void moveDisk(Stack towerOrigin, Stack towerDestiny) {
        int origin = towerOrigin.peek();
        int destin = towerDestiny.peek();

        if(origin < destin || destin == 0) {
            towerDestiny.push(towerOrigin.pop());
            System.out.println("Move disk "+origin+" from tower "+towerOrigin.getId()+" to "+towerDestiny.getId());
        }
        else {
            System.out.println("ERROR: Invalid move of disk "+origin+" from tower "+towerOrigin.getId()+" "+towerDestiny.getId());
            System.exit(0);
        }
    }



     //number of disks
     //towerOrigin origin tower
     //towerDestiny destiny tower
     //towerAux auxiliary tower
    public void moverNDisks(int n, Stack towerOrigin, Stack towerDestiny, Stack towerAux) {
        if(n > 1) {
            moverNDisks(n-1, towerOrigin, towerAux, towerDestiny);
            moveDisk(towerOrigin, towerDestiny);
            moverNDisks(n-1, towerAux, towerDestiny, towerOrigin);
        }
        else {
            moveDisk(towerOrigin, towerDestiny);
        }
    }

    /**
     * Resolv the hanoi tower problem
     */
    public void resolv() {
        moverNDisks(nDisks, towers[0], towers[2], towers[1]);
    }

    @Override
    public String toString() {
        String s = "";
        for(int i=0; i < 3; i++) {
            s+= ("Tower "+towers[i].getId()+": "+towers[i].toString()+"\n");
        }
        return s;
    }
}

