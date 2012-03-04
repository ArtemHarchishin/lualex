-- Classic hello program.
print("hello")

-- Single line comments in Lua start with double hyphen.
--[==[ Multiple line comments start
with double hyphen and two square brackets.
  and end with two square brackets. ]==]

c=nil

a, b, c, d,e,f = 1.2, 1.2E+1, .2E-2, -1E0, 1

one_two_3 = 123 -- is valid varable name

a="single 'quoted' string and double \"quoted\" string inside"
b='single \'quoted\' string and double "quoted" string inside'
c= [[ multiple line
with 'single'
and "double" quoted strings inside.]]

a,b,c,d,e = 1, 0xF87, "three", "four", 5
a,b,c,d,e = 1, 1.123, 1E9, -123, .0008
print("a="..a, "b="..b, "c="..c, "d="..d, "e="..e)

io.write("Hello from Lua!")

c={"a","b","c"} -- creates a table containing strings a,b,c

address={} -- empty address
address.Street="Wyman Street"
address.StreetNumber=360
address.AptNumber="2a"
print(address.StreetNumber, address["AptNumber"])

if c==1 then
    print("c is 1")
elseif c==2 then
    print("c is 2")
else
    print("c isn't 1 or 2, c is "..tostring(c))
end

b=(a==1) and "one" or "not one"

while a~=5 do -- Lua uses ~= to mean not equal
    a=a+1
    io.write(a.." ")
end

repeat
    a=a+1
    print(a)
until not a>=5

for key,value in pairs({1,2,3,4}) do print(key, value) end

function mySecondLuaFunction()
    return "string from my second function"
end

a,b,c,d,e,f = myFirstLuaFunctionWithMultipleReturnValues(1,2,"three")

function myfunc()
    local b=" local variable"
end

print(math.sqrt(9), math.pi)
print(string.upper("lower"),string.rep("a",5),string.find("abcde", "cd"))
table.sort(a,function(v1,v2) return v1 >= v2 end)

require( "iuplua" )
ml = iup.multiline
    {
    expand="YES",
    value="Quit this multiline edit app to continue Tutorial!",
    border="YES"
    }
dlg = iup.dialog{ml; title="IupMultiline", size="QUARTERxQUARTER",}
dlg:show()
print("Exit GUI app to continue!")
iup.MainLoop()

-- some errors
a = 89bbx
c = ~`
d = '3232
e = [==[
long line
but unfinished
]==
d = 3

