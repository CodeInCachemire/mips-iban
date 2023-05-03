	.data
	.globl modulo_str
	.text

# --- modulo_str ---
# Arguments:
# a0: start address of the buffer
# a1: number of bytes in the buffer
# a2: divisor
# Return:
# v0: the decimal number (encoded using ASCII digits '0' to '9') in the buffer [$a0 to $a0 + $a1 - 1] modulo $a2 
modulo_str:
	# TODO
	addi $t0, $a0, 0   # load address of the buffer
	addi $t1,$0,0 #counter
	move $t5,$a2  #we move divisor to t5
	
	addi $t3, $t3, 0 #our result hold
loop_modulo:
	lb $t2, 0($t0) #load first character into t2
	addi $t1, $t1, 1       # increment counter LOOP Counter
    	addi $t0, $t0, 1  	#increment address
    	
    	#here is modulo
    	mul $t3,$t3,10
    	addu $t3,$t3,$t2
	remu $t3,$t3,$t5
	
	bne $t1, $a1, loop_modulo 
	
	
	move $v0,$t3
	
	
	jr	$ra
