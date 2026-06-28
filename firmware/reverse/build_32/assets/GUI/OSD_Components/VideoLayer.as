class GUI.OSD_Components.VideoLayer extends MovieClip
{
   var __gpdb;
   var __imageParamName;
   var __mcPlot;
   var __plotPath;
   function VideoLayer()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__mcPlot = this.createEmptyMovieClip("mcPlot",this.getNextHighestDepth());
      this.LoadPlot(this.__gpdb.paramGet(this.__imageParamName));
      this.addCallbacks();
   }
   function addCallbacks()
   {
      this.__gpdb.addCallback(this.__imageParamName,mx.utils.Delegate.create(this,this.update));
   }
   function update(name, value)
   {
      this.__plotPath = value;
      this.paint();
   }
   function LoadPlot(pathname)
   {
      this.__plotPath = pathname;
      this.paint();
   }
   function paint()
   {
      if(_global.VxCapability("DEMO_SCREENS") && this.__plotPath != undefined && this.__plotPath != "")
      {
         _global.VxLog("VideoLayer::paint() loading \'" + this.__plotPath + "\'...");
         this.__mcPlot.loadMovie(this.__plotPath);
         this.__mcPlot._visible = true;
         this._visible = true;
      }
      else
      {
         this._visible = false;
      }
   }
   function Hide()
   {
      this._visible = false;
   }
   function Show()
   {
      this._visible = true;
   }
}
