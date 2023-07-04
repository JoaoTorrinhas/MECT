	.data
values:	.word 1,2,3,4,5,6,7,8,9,10
nelem:	.word 10
	.text
	.global main

main:
	addi r1,r0,nelem	;r1 = nelem
	nop
	nop
	lw r1,0(r1)		;r1 = nelem = 10
	addi r2,r0,values	;r2 = &values[0]
	addi r3,r0,0		;r3 = i = 0
	addi r8,r1,-1		;r8 = nelem - 1
	nop
	nop
for1:
	slt r9,r3,r8		;for(i = 0; i < nelem-1;i++){
	nop
	beqz r9,endloop1
	nop
	nop
	addi r5,r3,1		;	j = i+1
	lw r4,0(r2)		;	val(values[i])
	addi r6,r2,4		;	add(values[j])

for2:	slt r9,r5,r1		;	for(j = i+1; j < nelem; j++){
	nop
	beqz r9,endloop2
	nop
	nop
	lw r7,0(r6)		;		val(values[j])
	nop
	slt r9,r4,r7		;		if(val(values[i]) < val(values[j])){
	nop
	beqz r9,endIf		;
	nop
	nop
	add r9,r0,r4		;			tmp = val(values[i])
	add r4,r0,r7		;			values[i] = values[j]				
	add r7,r0,r9		;			values[j] = tmp
	nop			
	sw 0(r2),r4
	nop			
	sw 0(r6),r7					
				;		}
endIf:
	addi r5,r5,1		;	j++
	nop
	addi r6,r6,4		;	values[j]		
	j for2			;	}	
	nop
	nop
endloop2:	
	addi r3,r3,1		;i++
	addi r2,r2,4		;r2 = values[i]
	j for1
	nop
	nop
				;}
endloop1:
	trap 0
