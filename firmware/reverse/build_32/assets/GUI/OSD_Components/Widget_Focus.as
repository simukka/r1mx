class GUI.OSD_Components.Widget_Focus
{
   var __DISTANCE;
   var __INFINITY;
   var __gpdb;
   var __meter;
   var unit;
   function Widget_Focus()
   {
      this.__gpdb = _global.gpdb;
      this.unit = this.__gpdb.paramGet("GUI.USER_PREF.LENS_UNITS");
      this.SetFocus(this.__gpdb.paramGetNumber("SYSTEM.DEV.LENS.FEEDBACK.FOCUS"));
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("SYSTEM.DEV.LENS.FEEDBACK.FOCUS",_loc2_);
      this.__gpdb.addCallback("GUI.USER_PREF.LENS_UNITS",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "SYSTEM.DEV.LENS.FEEDBACK.FOCUS":
            this.SetFocus(this.__gpdb.paramGetNumber("SYSTEM.DEV.LENS.FEEDBACK.FOCUS"));
            return;
         case "GUI.USER_PREF.LENS_UNITS":
            this.unit = this.__gpdb.paramGet("GUI.USER_PREF.LENS_UNITS");
            this.SetFocus(this.__gpdb.paramGetNumber("SYSTEM.DEV.LENS.FEEDBACK.FOCUS"));
            return;
         default:
            return;
      }
   }
   function SetFocus(distance)
   {
      var _loc9_ = distance == 1677721;
      var _loc3_;
      var _loc8_;
      var _loc7_;
      var _loc10_;
      var _loc11_;
      var _loc5_;
      var _loc4_;
      if(_loc9_)
      {
         this.__INFINITY._visible = true;
         this.__DISTANCE._visible = false;
         this.__meter._visible = false;
      }
      else
      {
         if(this.unit == "METRIC")
         {
            _loc8_ = distance / 100;
            _loc3_ = _global.ShowDecimalPlaces(_loc8_,2,true);
            if(_loc3_.indexOf(".") > -1)
            {
               _loc7_ = _loc3_.split(".",2);
               _loc3_ = _loc7_[0] + "," + _loc7_[1];
            }
            this.__meter._visible = true;
            this.__DISTANCE.text = _loc3_;
            _loc10_ = this.__DISTANCE.getTextFormat();
            _loc11_ = _loc10_.getTextExtent(this.__DISTANCE.text).width;
            this.__meter._x = this.__DISTANCE._x + _loc11_ + 3;
         }
         else
         {
            _loc5_ = distance % 12;
            _loc4_ = (distance - _loc5_) / 12;
            if(_loc4_ > 10 || _loc5_ == 0)
            {
               _loc3_ = _loc4_.toString() + "\'";
            }
            else
            {
               _loc3_ = _loc4_.toString() + "\' " + _loc5_.toString() + "\"";
            }
            this.__meter._visible = false;
            this.__DISTANCE.text = _loc3_;
         }
         this.__INFINITY._visible = false;
         this.__DISTANCE._visible = true;
      }
   }
}
