# !expected
# VAR1:1:ru,en
# .PHONY:2:ru,fr
# !
# .. charset=koi8-r

# .. lang=ru
# ���������� ����� 1
# ������������ ������
# .. lang=en
# Variable number 1
# Used first
VAR1 = "Some variable"

# comment not used
# .. lang=ru
# phony target
.PHONY:

# target without any special comments
doctarget: .PHONY

