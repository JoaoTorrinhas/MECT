array:	.word 1,2,3,4,5,6,7,8,9,10
sum:	.space 4

.global main
main:
	addi r1, r0, 10 	;r1=10 size of the array
	addi r2, r0, 0		;r2=0, indice i=0
	addi r3, r0, 0 	 	; counter = 0
	addi r4, r0, array	;r4 = array[0]

loop1:
	slt r5,r2,r1		;for(int i = 0; i < 10; i++)
	beqz r5,endloop
	lw r6, 0(r4)		;r6 = value of array[i]
	nop
	add r3, r3, r6		;counter = counter + r6
	addi r4, r4, 4		; r4 = array[i], word ocupa 4 bytes
	addi r2, r2, 1		;i++
	j loop1			;jump back to the loop
endloop:
	addi r7, r0, sum	;add(sum)
	sw 0(r7),r3
	trap 0			;end of the programm
