class GUI.OSD_Components.HudUpperMC extends MovieClip
{
   var __gpdb;
   function HudUpperMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR HudUpperMC()");
      this.__gpdb = _global.gpdb;
      this._visible = this.__gpdb.paramGetBoolean("GUI.OSD.SHOW.UPPER_HUD");
      this.AddGpdbCallbacks();
   }
   function AddGpdbCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.OSD.SHOW.UPPER_HUD",_loc2_);
   }
   function Update(name, value)
   {
      _global.VxLog("HudUpperMC::Update(" + name + ", \'" + value + "\')");
      var _loc0_;
      if((_loc0_ = name) === "GUI.OSD.SHOW.UPPER_HUD")
      {
         this._visible = "true" == value;
      }
   }
}
