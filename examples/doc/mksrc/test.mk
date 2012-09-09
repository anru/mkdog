
# .. lang=ru
# Переменная номер 1
# Используется первой
# .. lang=en
# Variable number 1
# Used first
VAR1 = "Some variable"

# comment not used
# .. lang=ru
# phony target
# впп
# :make:var:`VAR1`
# fg
.PHONY:

# target without any special comments
doctarget: .PHONY

