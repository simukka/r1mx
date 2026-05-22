class GUI.OSD_Components.Widget_TCJamSyncMC extends MovieClip
{
   var __gpdb;
   function Widget_TCJamSyncMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.Show("true" == this.__gpdb.paramGet("SYSTEM.DEV.TIMECODE.JAMSYNC.ACTIVE"));
      this.AddCallbacks();
   }
   function Show(show)
   {
      this._visible = show;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("SYSTEM.DEV.TIMECODE.JAMSYNC.ACTIVE",_loc2_);
   }
   function Update(name, value)
   {
      var _loc0_ = null;
      if((_loc0_ = name) === "SYSTEM.DEV.TIMECODE.JAMSYNC.ACTIVE")
      {
         this.Show(value == "true");
      }
   }
}
