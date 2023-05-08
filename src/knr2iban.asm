	.data
	.globl knr2iban
	.text
# -- knr2iban
# Arguments:
# a0: IBAN buffer (22 bytes)
# a1: BLZ buffer (8 bytes)
# a2: KNR buffer (10 bytes)
knr2iban:
	# TODO
li $t0, 'D'
sb $t0, 0($a0)
li $t1, 'E'
sb $t1, 1($a0)
li $t0, '0'
sb $t0, 2($a0)
sb $t0, 3($a0)

li $t0, 0
li $t3, 0
addi $t0, $a1, 0  #address of blz to use
#loop blz-copy from iban2knr
addi $t3, $a0, 4   # address of the 5th character
addi $t1, $zero, 1    # initialize counter to 0

loop_blzrev:
    lb $t2, 0($t0)         # load character at current address into $t2
    sb $t2, 0($t3)         # store target buffer
    addi $t1, $t1, 1       # increment counter
    addi $t0, $t0, 1       # increment address by one to move to next byte address
    addi $t3, $t3, 1       # increment t buffer address
    bne $t1, 9, loop_blzrev   # loop condition
   
li $t0, 0
li $t3, 0
li $t3, 0
addi $t0, $a2, 0  #address of blz to use
#loop blz-copy from iban2knr
addi $t3, $a0, 12   # address of the 5th character
addi $t1, $zero, 0    # initialize counter to 0

loop_knrrev:
    lb $t2, 0($t0)         # load character at current address into $t2
    sb $t2, 0($t3)         # store target buffer
    addi $t1, $t1, 1       # increment counter
    addi $t0, $t0, 1       # increment address by one to move to next byte address
    addi $t3, $t3, 1       # increment t buffer address
    bne $t1, 10, loop_knrrev   # loop condition	
    
#addi $t,$a0, -22	
addi $sp,$sp,-12
sw $a0, 8($sp)
sw $ra, 4($sp)

jal validate_checksum

lw $a0, 8($sp)
lw $ra, 4($sp)
addi $sp,$sp, 12
#check digits is 98-$v0
li $t4,0
li $t1,0
li $t4,98
sub $t4,$t4,$v0
div  $t4,$t4, 10		
mfhi $t1         # rem
addi $t4, $t4, 48
addi $t1, $t1, 48 #quo

addi $t7,$a0,0   	
sb $t4, 2($t7)
sb $t1,	3($t7)



jr	$ra
