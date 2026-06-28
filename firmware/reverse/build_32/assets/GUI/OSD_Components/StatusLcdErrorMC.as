class GUI.OSD_Components.StatusLcdErrorMC extends MovieClip
{
   var __ERROR;
   var __bodyOverTemp;
   var __gpdb;
   var __intervalID;
   var __sensorOverTemp;
   function StatusLcdErrorMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR StatusLcdErrorMC()");
      this.__gpdb = _global.gpdb;
      this.__intervalID = null;
      this._visible = false;
      this.__sensorOverTemp = "true" == this.__gpdb.paramGet("SYSTEM.THERMAL.SENSOR_OVERTEMP");
      this.__bodyOverTemp = "true" == this.__gpdb.paramGet("SYSTEM.THERMAL.BODY_OVERTEMP");
      this.addCallbacks();
      this.Paint();
   }
   function Paint()
   {
      if(this.__bodyOverTemp)
      {
         this.__ERROR.text = "Body Hot";
         this.FlashPanel(true);
      }
      else if(this.__sensorOverTemp)
      {
         this.__ERROR.text = "Sensor Hot";
         this.FlashPanel(true);
      }
      else
      {
         this.__ERROR.text = "";
         this.FlashPanel(false);
      }
   }
   function FlashPanel(active)
   {
      if(active)
      {
         this._visible = true;
         if(this.__intervalID == null)
         {
            this.__intervalID = setInterval(this,"handleRuntimeTimer",2000);
         }
      }
      else
      {
         clearInterval(this.__intervalID);
         this.__intervalID = null;
         this._visible = false;
      }
   }
   function handleRuntimeTimer()
   {
      this._visible = !this._visible;
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("SYSTEM.THERMAL.SENSOR_OVERTEMP",_loc2_);
      this.__gpdb.addCallback("SYSTEM.THERMAL.BODY_OVERTEMP",_loc2_);
   }
   function update(name, value)
   {
      switch(name)
      {
         case "SYSTEM.THERMAL.SENSOR_OVERTEMP":
            this.__sensorOverTemp = value == "true";
            this.Paint();
            return;
         case "SYSTEM.THERMAL.BODY_OVERTEMP":
            this.__bodyOverTemp = value == "true";
            this.Paint();
            return;
         default:
            return;
      }
   }
}
