	.data
	myarrayiban: .space 25
	array: .space 8
	.globl validate_checksum
	.text

# -- validate_checksum --
# Arguments:
# a0 : Address of a string containing a german IBAN (22 characters)
# Return:
# v0 : the checksum of the IBAN
validate_checksum:
	# TODO

addi $t2,$a0,0
li $t8, 10
la $t7,array #131489
la $t6, myarrayiban
addi $t9,$t7,0
#for D char
	lb $t0, ($t2)
	subu $t0 $t0 55
	div $t0, $t8
	mflo $t3 #quotient
	add $t3, $t3,48
	sb $t3, 0($t9)
	mfhi $t4 #remainder in 
	add $t4,$t4,48
	sb $t4, 1($t9)
	li $t0,0
#for t1
	lb $t0, 1($t2)
	subu $t0 $t0 55
	div  $t0, $t8
	mflo $t3 #quotient
	add $t3,$t3,48
	sb $t3, 2($t9)
	mfhi $t4 #remainder in 
	add $t4,$t4,48
	sb $t4, 3($t9)

lb $t0, 2($t2)
#sub $t0, $t0, 48      # load the 3rd digit from IBAN buffer into $t1
sb $t0, 4($t9) 

lb $t0, 3($t2)
#sub $t0, $t0, 48       # load the 3rd digit from IBAN buffer into $t1
sb $t0, 5($t9) 

  
# copy 5th to 22nd digits to temp buffer
    addi $t2, $a0, 4    # pointer to 5th digit (start counting from 0)
    addi $t3, $t6, 0    # pointer to start of temp buffer
    li $t4, 18          # loop counter (22 - 5 + 1 = 18)
  loop: #this will be done with $a0
    lb $t5, ($t2)       # load byte from IBAN
    sb $t5, ($t3)       # store byte in temp buffer
    addi $t2, $t2, 1    # increment IBAN pointer
    addi $t3, $t3, 1    # increment temp buffer pointer
    addi $t4, $t4, -1   # decrement loop counter
    bne $t4, $zero, loop # repeat until all digits are copied
    #addi $t3, $t3, 1
    #sb $zero, ($t3)
################################################################################3
lb $t0, 0($t7)
sb $t0, 18($t6)
lb $t0, 1($t7)
sb $t0, 19($t6)
lb $t0, 2($t7)
sb $t0, 20($t6)
lb $t0, 3($t7)
sb $t0, 21($t6)
lb $t0, 4($t7)
sb $t0, 22($t6)
lb $t0, 5($t7)
sb $t0, 23($t6)
#addi $t3, $t3, 1
sb $zero, 24($t6)   	

subi $sp,$sp,-12
sw $t6, 0($sp)
sw $a0, 4($sp)
move $a0,$t6
sw $ra, 8($sp)
addi $a1, $zero, 24
addi $a2, $zero, 97
jal modulo_str
lw $t6,0($sp)
lw $a0,4($sp)
lw $ra,8($sp)
	
jr	$ra
