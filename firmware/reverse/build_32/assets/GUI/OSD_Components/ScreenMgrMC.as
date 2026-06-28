class GUI.OSD_Components.ScreenMgrMC extends MovieClip
{
   var __activeScreen;
   var __screens;
   static var __manager;
   function ScreenMgrMC()
   {
      super();
      _global.VxDebug("...........................................................................CTOR ScreenMgrMC()");
      GUI.OSD_Components.ScreenMgrMC.__manager = this;
      this.__screens = new Object();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.ScreenMgrMC.__manager === undefined)
      {
         _global.VxError("ERROR! ScreenMgrMC::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.ScreenMgrMC.__manager;
   }
   function AttachScreen(mcName, lcdBanner, parent)
   {
      var _loc5_ = mcName;
      parent = parent != undefined ? parent : this;
      parent.attachMovie(mcName,_loc5_,parent.getNextHighestDepth(),{__lcdBanner:lcdBanner});
      this.__screens[mcName] = GUI.OSD_Components.FullScreenMC(parent[_loc5_]);
      if(this.__screens[mcName] == undefined)
      {
         _global.VxError("ScreenMgrMC::AttachScreen(" + mcName + "): No screen created!");
      }
      return this.__screens[mcName];
   }
   function MarkActive(scrnName, activate)
   {
      _global.VxDebug("ScreenMgrMC::MarkActive(" + scrnName + ", " + activate + ")");
      if(activate)
      {
         if(this.__activeScreen != "")
         {
            this.__screens[this.__activeScreen].Deactivate(false);
         }
         this.__activeScreen = scrnName;
         GUI.OSD_Components.TabManager.GetManager().SetScreenToReceiveInputFocus(this.__screens[this.__activeScreen]);
      }
      else if(scrnName == this.__activeScreen)
      {
         this.__activeScreen = "";
         GUI.OSD_Components.TabManager.GetManager().SetScreenToReceiveInputFocus(this.__screens[this.__activeScreen]);
      }
   }
   function IsScreenActive()
   {
      var _loc3_ = !(this.__activeScreen == undefined || this.__activeScreen == "");
      _global.VxDebug("ScreenMgrMC.IsScreenActive() isScreenActive: " + _loc3_ + ", __activeScreen: " + this.__activeScreen);
      return _loc3_;
   }
   function GetScreen(mcName)
   {
      var _loc3_ = this.__screens[mcName];
      if(_loc3_ == undefined)
      {
         _global.VxError("ScreenMgrMC::GetScreen(" + mcName + ") screen UNDEFINED.");
      }
      return _loc3_;
   }
   function Activate(mcName, arg0, arg1)
   {
      if(this.__activeScreen != undefined && this.__activeScreen != "")
      {
         this.__screens[this.__activeScreen].Deactivate();
      }
      var _loc3_ = this.__screens[mcName];
      if(_loc3_ == undefined)
      {
         _global.VxError("ScreenMgrMC::Activate(" + mcName + ") screen UNDEFINED. Ignoring.");
      }
      else
      {
         _loc3_.Activate(arg0,arg1);
         this.__activeScreen = mcName;
         this._visible = true;
      }
      return _loc3_;
   }
   function Deactivate(mcName)
   {
      mcName = mcName != undefined ? mcName : this.__activeScreen;
      this.__screens[mcName].Deactivate(true);
      this.__activeScreen = "";
   }
   function DisplayScreen(mcName)
   {
      _global.VxDebug("ScreenMgrMC::DisplayScreen(\'" + mcName + "\') object: " + this.__screens[mcName]);
      GUI.OSD_Components.MenuManager.GetManager().ExitMenuTree();
      this._visible = true;
      this.__screens[mcName].Activate();
      return this.__screens[mcName];
   }
   function NewScreen(mcName)
   {
      if(this.__screens[mcName] == undefined)
      {
         this.attachMovie("FullScreenMC",mcName,this.getNextHighestDepth(),{_x:0,_y:0});
         this.__screens[mcName] = this[mcName];
         this.__screens[mcName]._visible = false;
      }
      else
      {
         _global.VxError("ERROR! ScreenMgrMC::NewScreen(\'" + mcName + "\') screen already exists!");
      }
      return this.__screens[mcName];
   }
}
