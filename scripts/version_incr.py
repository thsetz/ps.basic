data = open("VERSION.txt").read()
ver, rev, mino = data.split('.')

new_version = ver + '.' + rev + '.' + str(int(mino)+1)  # result: '1.10'
print("OLD VERSION WAS %s NEW_VERSION IS %s"%(data,new_version))
fp = open("VERSION.txt","w")
fp.write(new_version)
fp.close()

