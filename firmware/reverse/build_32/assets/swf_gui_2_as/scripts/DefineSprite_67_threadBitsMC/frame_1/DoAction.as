function RandRange(min, max)
{
   var _loc1_ = Math.floor(Math.random() * (max - min + 1)) + min;
   return _loc1_;
}
var bits = RandRange(0,255);
var bit0 = bits & 1;
var bit1 = (bits >>>= 1) & 1;
var bit2 = (bits >>>= 1) & 1;
var bit3 = (bits >>>= 1) & 1;
var bit4 = (bits >>>= 1) & 1;
var bit5 = (bits >>>= 1) & 1;
var bit6 = (bits >>>= 1) & 1;
var bit7 = (bits >>>= 1) & 1;
text = bit0 + "\r" + bit1 + "\r" + bit2 + "\r" + bit3 + "\r" + bit4 + "\r" + bit5 + "\r" + bit6 + "\r" + bit7;
