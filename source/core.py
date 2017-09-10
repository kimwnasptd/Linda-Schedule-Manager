Days    =   ['Monday','Thuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
Months  =   ['July','August','September','Octomber','November','December','January','February','March','April','May','June']

inp = int(input())
print("Month: " + str(Months[int(inp / (30 * 24))]))
print("Day: " + str(Days[int(inp / 24)]))
