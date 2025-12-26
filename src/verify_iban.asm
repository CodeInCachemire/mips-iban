    .data
    .globl verify_iban
    .text

# -- verify_iban --
# Arguments:
# a0 : address of IBAN buffer (22 bytes)
# Return:
# v0 = 0 → valid
# v0 = 1 → invalid prefix
# v0 = 2 → invalid checksum
verify_iban:
    # --- prefix check: "DE" ---
    lb   $t0, 0($a0)
    li   $t1, 'D'
    bne  $t0, $t1, prefix_error

    lb   $t0, 1($a0)
    li   $t1, 'E'
    bne  $t0, $t1, prefix_error

    # --- checksum check ---
    addi $sp, $sp, -4
    sw   $ra, 0($sp)

    jal  validate_checksum

    lw   $ra, 0($sp)
    addi $sp, $sp, 4

    li   $t0, 1
    beq  $v0, $t0, valid_iban

    # checksum invalid
    li   $v0, 2
    jr   $ra

prefix_error:
    li   $v0, 1
    jr   $ra

valid_iban:
    li   $v0, 0
    jr   $ra
