class GUI.GPDB.GPdbParam
{
   var __callbackList;
   var __cbStack;
   var __dirty;
   var __flags;
   var __gpdb;
   var __label;
   var __name;
   var __revertValue;
   var __type;
   var __value;
   var options;
   var __isEvent = false;
   function GPdbParam(gpdb, name, type, value)
   {
      this.__gpdb = gpdb;
      this.__name = name;
      this.__type = type;
      this.__value = value;
      this.__dirty = false;
      this.__flags.Event = false;
      this.__cbStack = new Array();
      this.options = new GUI.GPDB.ParamOptions(gpdb,this);
   }
   function get name()
   {
      return this.__name;
   }
   function set name(name)
   {
      this.__name = name;
   }
   function get type()
   {
      return this.__type;
   }
   function set type(type)
   {
      this.__type = type;
   }
   function get value()
   {
      return this.__value;
   }
   function set value(value)
   {
      var _loc4_ = value != this.__value;
      this.__dirty |= _loc4_;
      var _loc5_;
      if(_loc4_ || this.isEvent())
      {
         _loc5_ = !this.isEvent() ? "" : "[EVENT]";
         switch(this.__type)
         {
            case "integer":
            case "float":
               if(value == NaN)
               {
                  throw new Error("GPdbParam.set.value(" + this.__name + ", " + value + ") is not a valid integer/float");
               }
               this.__value = value.toString();
               break;
            case "boolean":
               this.__value = value;
               break;
            default:
               this.__value = value;
         }
         this.__label = this.__value;
         if(this.__gpdb.callbacksEnabled)
         {
            this.EnvokeLocalCallbacks();
         }
      }
   }
   function extractNumber(s)
   {
      var _loc1_ = 0;
      while(s.charAt(_loc1_) == " ")
      {
         _loc1_ = _loc1_ + 1;
      }
      if(_loc1_ > 0)
      {
         s = s.slice(_loc1_);
      }
      var _loc3_ = s.indexOf(" ");
      if(_loc3_ > 0)
      {
         s = s.substring(0,_loc3_);
      }
      return Number(s);
   }
   function get label()
   {
      return this.__label;
   }
   function set label(label)
   {
      this.__label = label;
   }
   function EnvokeLocalCallbacks()
   {
      var _loc3_;
      if(this.__callbackList.length > 0)
      {
         _global.VxLogWvEvent(2,"GPDB(" + this.__name + ", " + this.__value + ")");
      }
      var _loc4_ = this.__callbackList.length;
      while(_loc4_ > 0)
      {
         _loc3_ = new Object();
         _loc3_.fnc = this.__callbackList[_loc4_ - 1];
         _loc3_.name = this.__name;
         _loc3_.value = this.__value;
         this.__cbStack.push(_loc3_);
         _loc4_ = _loc4_ - 1;
      }
      while(this.__cbStack.length > 0)
      {
         _loc3_ = this.__cbStack.pop();
         _loc3_.fnc(_loc3_.name,_loc3_.value);
         false;
      }
   }
   function commit()
   {
      this.__revertValue = this.__value;
   }
   function revert()
   {
      this.__value = this.__revertValue;
      this.value = this.__value;
   }
   function get dirty()
   {
      return this.__dirty;
   }
   function set dirty(dirty)
   {
      this.__dirty = dirty;
   }
   function isEvent()
   {
      return this.__flags.Event;
   }
   function isFlag(flag)
   {
      if(this.__flags[flag] != undefined)
      {
         return true;
      }
      return false;
   }
   function addFlag(flag)
   {
      if(this.__flags == null)
      {
         this.__flags = new Object();
      }
      this.__flags[flag] = true;
   }
   function addCallback(fnc)
   {
      if(this.__callbackList == null)
      {
         this.__callbackList = new Array();
      }
      this.__callbackList.push(fnc);
   }
   function NumberOfCallbacks()
   {
      return this.__callbackList.length;
   }
}
