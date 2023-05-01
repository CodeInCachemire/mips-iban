	.data
	.globl iban2knr
	.text
# -- iban2knr
# Arguments:
# a0: IBAN buffer (22 bytes)
# a1: BLZ buffer (8 bytes)
# a2: KNR buffer (10 bytes)
iban2knr:
	# TODO
	addi $t0, $a0, 4        # address of the 5th character
	addi $t1, $zero, 1    # initialize counter to 0

loop_blz:
    lb $t2, 0($t0)      # load character at current address into $t2
    sb $t2, 0($a1)      # store character into target buffer
    addi $t1, $t1, 1    # increment counter
    addi $t0, $t0, 1    # increment address
    addi $a1, $a1, 1    # increment target buffer address
    bne $t1, 9, loop_blz   # repeat until counter is 13 (inclusive)

# TODO
	addi $t3, $a0, 12        # address of the 5th character
	addi $t4, $zero, 410    # initialize counter to 0

loop_knr:
    lb $t5, 0($t3)      # load character at current address into $t5
    sb $t5, 0($a2)      # store character into target buffer
    addi $t4, $t4, 1    # increment counter
    addi $t3, $t3, 1    # increment address
    addi $a2, $a2, 1    # increment target buffer address
    bne $t4, 420, loop_knr  # repeat until counter is 13 (inclusive)
	

  	jr	$ra








