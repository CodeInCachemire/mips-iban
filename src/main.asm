	.data
	.globl main
# constants
greeterstr:
	.asciiz "IBAN <-> KNR+BLZ Conversion\n1.) IBAN to KNR+BLZ\n2.) KNR+BLZ to IBAN\nInput:"
destr:
	.asciiz "DE"
invalidstr:
	.asciiz "Invalid input!\n"
ibanstr:
	.asciiz "IBAN:"
knrstr:
	.asciiz "KNR:"
blzstr:
	.asciiz "BLZ:"
newlinestr:
	.asciiz "\n"
zzstr:
	.asciiz "00"
emptystr:
	.asciiz ""
msg_checksum_ok:
    .asciiz "MSG=Valid checksum! This is a valid IBAN!\n"
msg_checksum_bad:
    .asciiz "MSG=Invalid checksum, this is not a valid IBAN!\n"
msg_prefix_bad:
    .asciiz "MSG=No german IBAN prefix!\n"
# local character buffers
# we allocate one additional byte for the null terminator
knrbuf:
	.space 11
blzbuf:
	.space 9
ibanbuf:
	.space 23
HEADLESS:
    .word 1

modebuf:
    .space 8      # enough for "IBAN\n" or "KNRBLZ\n"

okstr:
    .asciiz "OK\n"
errstr:
    .asciiz "ERR\n"
msg_invalid:
    .asciiz "MSG=Invalid input\n"
blz_key:
    .asciiz "BLZ="
knr_key:
    .asciiz "KNR="
iban_key:
    .asciiz "IBAN="
	.text
# wait for input
main:
    lw  $t0 HEADLESS
    beq $t0 $zero interactive_mode #mars simulator mode
    j   headless_mode

interactive_mode:
    la  $a0 greeterstr
    jal print
    j   menu
menu:
	li	$v0 5
	syscall
	beq	$v0 1 menu_iban_to_knr
	beq	$v0 2 menu_knr_to_iban
  
	la	$a0 invalidstr
	jal	print
	j	end

menu_iban_to_knr:
# read IBAN 
	la	$a0 ibanstr
	jal	print
	la	$a0 ibanbuf
	li	$a1 22
	jal	readbuf
# check IBAN 
	la	$a0 ibanbuf
	# jal verify_iban
	# la	$a0 deprefix_errmsg
	# beq	$v0 1 error
	# la	$a0 checksum_errmsg
	# beq	$v0 2 error
	# la	$a0 checksumok_msg
	# jal	println

# call iban_to_knr
	la	$a0 ibanbuf
	la	$a1 blzbuf
	la	$a2 knrbuf
	jal	iban2knr
  
# print KNR
	la	$a0 knrstr
	jal	print
	la	$a0 knrbuf
	jal	println
  
# print BLZ
	la	$a0 blzstr
	jal	print
	la	$a0 blzbuf
	jal	println
  
# exit
	j	end


menu_knr_to_iban:
# read KNR 
	la	$a0 knrstr
	jal	print
	la	$a0 knrbuf
	li	$a1 10
	jal	readbuf
  
# read BLZ 
	la	$a0 blzstr
	jal	print
	la	$a0 blzbuf
	li	$a1 8
	jal	readbuf

	la	$a0 ibanbuf
	la	$a1 blzbuf
	la	$a2 knrbuf
	jal	knr2iban
  
# print IBAN 
	la	$a0 ibanstr
	jal	print
	la	$a0 ibanbuf
	jal	println
	j	end


headless_mode:
    # read mode line
    la  $a0 modebuf
    li  $a1 7
    jal readbuf

    # check if mode == "IBAN"
    la  $t0 modebuf
    lb  $t1 0($t0)
    lb  $t2 1($t0)
    lb  $t3 2($t0)
    lb  $t4 3($t0)
    li  $t5 'I'
    li  $t6 'B'
    li  $t7 'A'
    li  $t8 'N'
    beq $t1 $t5 check_IBAN2
    j   check_KNRBLZ

check_IBAN2:
    bne $t2 $t6 headless_error
    bne $t3 $t7 headless_error
    bne $t4 $t8 headless_error

    # read IBAN
    la $a0 ibanbuf
    li $a1 22
    jal readbuf

    #iban verification
    la $a0 ibanbuf
    jal verify_iban

	li  $t0 1
    beq $v0 $t0 headless_prefix_error
    li  $t0 2
    beq $v0 $t0 headless_checksum_error
    la  $a0 okstr
    jal print
	la	$a0 msg_checksum_ok
	jal	print

    # call iban2knr
    la  $a0 ibanbuf
    la  $a1 blzbuf
    la  $a2 knrbuf
    jal iban2knr

    #print blz and knr
    la  $a0 blz_key
    jal print
    la  $a0 blzbuf
    jal println

    la  $a0 knr_key
    jal print
    la  $a0 knrbuf
    jal println

    j end

check_KNRBLZ:
    lb  $t1 0($t0)
    lb  $t2 1($t0)
    lb  $t3 2($t0)
    lb  $t4 3($t0)
    lb  $t5 4($t0)
    lb  $t6 5($t0)

    li  $t7 'K'
    li  $t8 'N'
    li  $t9 'R'
    li  $s0 'B'
    li  $s1 'L'
    li  $s2 'Z'

    bne $t1 $t7 headless_error
    bne $t2 $t8 headless_error
    bne $t3 $t9 headless_error
    bne $t4 $s0 headless_error
    bne $t5 $s1 headless_error
    bne $t6 $s2 headless_error

    # read KNR
    la  $a0 knrbuf
    li  $a1 10
    jal readbuf

    # read BLZ
    la  $a0 blzbuf
    li  $a1 8
    jal readbuf

    # call knr2iban
    la  $a0 ibanbuf
    la  $a1 blzbuf
    la  $a2 knrbuf
    jal knr2iban

    # print result
    la  $a0 okstr
    jal print

    la  $a0 iban_key
    jal print
    la  $a0 ibanbuf
    jal println

    j end

headless_error:
    la  $a0 errstr
    jal print
    la  $a0 msg_invalid
    jal print
    j end

headless_prefix_error:
    la  $a0 errstr
    jal print
    la  $a0 msg_prefix_bad
    jal print
    j end

headless_checksum_error:
    la  $a0 errstr
    jal print
    la  $a0 msg_checksum_bad
    jal print
    j end