	.data
	.globl main
numberstr:
	.asciiz "4611686018427387904"
	.text
main:
	la	$a0 numberstr
	li	$a1 19
	la	$a2 63
	jal	modulo_str
	move	$a0 $v0
	li	$v0 1
	syscall
	li	$v0 10
	syscall
