from pyteal import *
def approval_program():
    return Approve()  # Placeholder
program = compileTeal(approval_program(), mode=Mode.Application, version=6)
