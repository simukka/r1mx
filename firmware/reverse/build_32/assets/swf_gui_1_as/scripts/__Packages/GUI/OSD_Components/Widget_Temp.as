class GUI.OSD_Components.Widget_Temp extends MovieClip
{
   var __gpdb;
   var __sensorOverTemp;
   var __sensorUnderTemp;
   var __bodyOverTemp;
   var __sensorAvgTemp;
   var __sensorA;
   var __sensorB;
   var __sensorC;
   var __sensorD;
   function Widget_Temp()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__sensorOverTemp = "true" == this.__gpdb.paramGet("SYSTEM.THERMAL.SENSOR_OVERTEMP");
      this.__sensorUnderTemp = "true" == this.__gpdb.paramGet("SYSTEM.THERMAL.SENSOR_UNDERTEMP");
      this.__bodyOverTemp = "true" == this.__gpdb.paramGet("SYSTEM.THERMAL.BODY_OVERTEMP");
      this.addCallbacks();
      this.paint();
   }
   function CalculateAverage()
   {
      this.__sensorAvgTemp = (this.__sensorA + this.__sensorB + this.__sensorC + this.__sensorD) / 4;
      return undefined;
   }
   function paint()
   {
      if(this.__bodyOverTemp)
      {
         this.gotoAndStop("FRAME_TEMP_OVER");
      }
      else if(this.__sensorOverTemp && this.__sensorAvgTemp != 100)
      {
         this.gotoAndStop("FRAME_TEMP_OVER");
      }
      else if(this.__sensorUnderTemp)
      {
         this.gotoAndStop("FRAME_TEMP_UNDER");
      }
      else
      {
         this.gotoAndStop("FRAME_TEMP_OK");
      }
   }
   function addCallbacks()
   {
      this.__gpdb.addCallback("SYSTEM.THERMAL.SENSOR_OVERTEMP",mx.utils.Delegate.create(this,this.update));
      this.__gpdb.addCallback("SYSTEM.THERMAL.SENSOR_UNDERTEMP",mx.utils.Delegate.create(this,this.update));
      this.__gpdb.addCallback("SYSTEM.THERMAL.BODY_OVERTEMP",mx.utils.Delegate.create(this,this.update));
   }
   function update(name, value)
   {
      switch(name)
      {
         case "SYSTEM.THERMAL.SENSOR_OVERTEMP":
            this.__sensorOverTemp = value == "true";
            this.paint();
            break;
         case "SYSTEM.THERMAL.SENSOR_UNDERTEMP":
            this.__sensorUnderTemp = value == "true";
            this.paint();
            break;
         case "SYSTEM.THERMAL.BODY_OVERTEMP":
            this.__bodyOverTemp = value == "true";
            this.paint();
            break;
         case "SYSTEM.THERMAL.SENSOR.SENSOR_A":
            this.__sensorA = Number(value);
            this.CalculateAverage();
            break;
         case "SYSTEM.THERMAL.SENSOR.SENSOR_B":
            this.__sensorB = Number(value);
            this.CalculateAverage();
            break;
         case "SYSTEM.THERMAL.SENSOR.SENSOR_C":
            this.__sensorC = Number(value);
            this.CalculateAverage();
            break;
         case "SYSTEM.THERMAL.SENSOR.SENSOR_D":
            this.__sensorD = Number(value);
            this.CalculateAverage();
      }
   }
}
