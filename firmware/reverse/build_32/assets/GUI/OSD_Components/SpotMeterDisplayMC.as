class GUI.OSD_Components.SpotMeterDisplayMC extends MovieClip
{
   var __IRE_B;
   var __IRE_G;
   var __IRE_R;
   var __IRE_V;
   var __gpdb;
   var __spotMeterReticle;
   var mcSpotMeterReticle;
   function SpotMeterDisplayMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__IRE_R.text = "0";
      this.__IRE_G.text = "0";
      this.__IRE_B.text = "0";
      this.__IRE_V.text = "0";
      this.attachMovie("SpotMeterReticleMC","mcSpotMeterReticle",this.getNextHighestDepth(),{_x:640,_y:424});
      this.__spotMeterReticle = this.mcSpotMeterReticle;
      this.Activate(false);
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Callback);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.SPOT_METER.VALUE",_loc2_);
   }
   function Callback(name, value)
   {
      var _loc0_;
      if((_loc0_ = name) !== "IMAGE_ANALYSIS.SPOT_METER.VALUE")
      {
         _global.VxError("SpotMeterDisplayMC:Callback() Unrecognized param \'" + name + "\'");
      }
      else
      {
         this.__IRE_V.text = value;
      }
   }
   function Activate(activate)
   {
      this._visible = activate;
      this.__spotMeterReticle.Activate(activate);
   }
   function onInputEvent(name, value)
   {
      return this.__spotMeterReticle.onInputEvent(name,value);
   }
}
