class GUI.OSD_Components.Border_848 extends MovieClip
{
   var __gpdb;
   function Border_848()
   {
      super();
      this.__gpdb = _global.gpdb;
      _global.VxDebug("...........................................................................CTOR Border_848()");
      this._visible = "true" == this.__gpdb.paramGet("DEBUG.BORDER_1280x848");
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Callback);
      this.__gpdb.addCallback("DEBUG.BORDER_1280x848",_loc2_);
   }
   function Callback(name, value)
   {
      var _loc0_ = null;
      if((_loc0_ = name) !== "DEBUG.BORDER_1280x848")
      {
         throw new Error("Border_848:Callback() Unrecognized param \'" + name + "\'");
      }
      this._visible = "true" == value;
   }
}
