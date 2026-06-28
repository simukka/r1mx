class GUI.OSD_Components.TabManager
{
   var __focused;
   var __fullScreen;
   var __gpdb;
   var __mc;
   var __targetStack;
   var __targets;
   static var __manager;
   static var EVENT_SELECT = "GUI.RAWINPUT.JOYSTICK.SELECT";
   static var EVENT_EXIT = "GUI.RAWINPUT.BUTTON.EXIT";
   static var EVENT_UNDO = "GUI.RAWINPUT.BUTTON.UNDO";
   static var EVENT_RIGHT = "GUI.RAWINPUT.JOYSTICK.E";
   static var EVENT_LEFT = "GUI.RAWINPUT.JOYSTICK.W";
   static var EVENT_UP = "GUI.RAWINPUT.JOYSTICK.N";
   static var EVENT_DOWN = "GUI.RAWINPUT.JOYSTICK.S";
   static var EVENT_NE = "GUI.RAWINPUT.JOYSTICK.NE";
   static var EVENT_SE = "GUI.RAWINPUT.JOYSTICK.SE";
   static var EVENT_SW = "GUI.RAWINPUT.JOYSTICK.SW";
   static var EVENT_NW = "GUI.RAWINPUT.JOYSTICK.NW";
   static var EVENT_CW = "GUI.RAWINPUT.JOYSTICK.CW";
   static var EVENT_CCW = "GUI.RAWINPUT.JOYSTICK.CCW";
   static var EVENT_CW_JUMP = "GUI.RAWINPUT.JOYSTICK.CW_JUMP";
   static var EVENT_CCW_JUMP = "GUI.RAWINPUT.JOYSTICK.CCW_JUMP";
   static var EVENT_EVF_SELECT = "SYSTEM.DEV.EVF.RAWINPUT.DIAL.SELECT";
   static var EVENT_EVF_CW = "SYSTEM.DEV.EVF.RAWINPUT.DIAL.CW";
   static var EVENT_EVF_CCW = "SYSTEM.DEV.EVF.RAWINPUT.DIAL.CCW";
   static var EVENT_EVF_UP = "SYSTEM.DEV.EVF.RAWINPUT.BUTTON.A";
   static var EVENT_EVF_DOWN = "SYSTEM.DEV.EVF.RAWINPUT.BUTTON.B";
   function TabManager()
   {
      _global.VxDebug("...........................................................................CTOR TabManager()");
      GUI.OSD_Components.TabManager.__manager = this;
      this.__targets = new GUI.OSD_Components.GizmoGrid();
      this.__targetStack = new Array();
      this.__focused = null;
      var _loc4_ = _root;
      var _loc5_ = "__tabManager";
      var _loc6_ = "TabManager";
      _loc4_.attachMovie(_loc6_,_loc5_,_loc4_.getNextHighestDepth());
      this.__mc = _loc4_[_loc5_];
      this.__mc._x = -500;
      Key.addListener(this);
      _focusrect = false;
      this.__gpdb = _global.gpdb;
      this.initGpdbCallbacks();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.TabManager.__manager === undefined)
      {
         _global.VxError("ERROR! TabManager::GetManager() called before being instantiated");
      }
      return GUI.OSD_Components.TabManager.__manager;
   }
   function initGpdbCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.handleEvent);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_SELECT,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_EXIT,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_UNDO,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_UP,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_DOWN,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_RIGHT,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_LEFT,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_NE,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_SE,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_SW,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_NW,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_CW,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_CW_JUMP,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_CCW,_loc2_);
      this.__gpdb.addCallback(GUI.OSD_Components.TabManager.EVENT_CCW_JUMP,_loc2_);
   }
   function handleEvent(name, value)
   {
      if(this.IsGuiNavigationActive())
      {
         this.ProcessGuiNavigation(name,value);
      }
      else if(this.IsFullScreenActive())
      {
         this.ProcessFullScreenEvent(name,value);
      }
      else
      {
         this.ProcessGadgetEvent(name,value);
      }
   }
   function IsFullScreenActive()
   {
      var _loc2_ = this.__fullScreen && this.__fullScreen.onInputEvent;
      return _loc2_;
   }
   function ProcessFullScreenEvent(name, value)
   {
      _global.VxDebug("TabManager::ProcessFullScreenEvent(" + name + ", " + value + ")");
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_EXIT:
         case GUI.OSD_Components.TabManager.EVENT_RIGHT:
         case GUI.OSD_Components.TabManager.EVENT_LEFT:
         case GUI.OSD_Components.TabManager.EVENT_UP:
         case GUI.OSD_Components.TabManager.EVENT_DOWN:
      }
      this.__fullScreen.onInputEvent(name,value);
   }
   function SetScreenToReceiveInputFocus(screen)
   {
      _global.VxDebug("TabManager::SetScreenToReceiveInputFocus(): " + screen);
      this.__fullScreen = screen;
   }
   function IsGuiNavigationActive()
   {
      return this.__focused && this.__focused.onInputEvent;
   }
   function ProcessGuiNavigation(name, value)
   {
      _global.VxDebug("TabManager::ProcessGuiNavigation(" + name + ", " + value + ")");
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_RIGHT:
         case GUI.OSD_Components.TabManager.EVENT_LEFT:
            this.NavigateGizmoGrid(name,value);
            return;
         case GUI.OSD_Components.TabManager.EVENT_UP:
         case GUI.OSD_Components.TabManager.EVENT_EXIT:
            GUI.OSD_Components.MenuManager.GetManager().onInputEvent(name,value);
            return;
         case GUI.OSD_Components.TabManager.EVENT_DOWN:
            this.__focused.onInputEvent(GUI.OSD_Components.TabManager.EVENT_SELECT,value != "0" ? "true" : "false");
            return;
         default:
            this.__focused.onInputEvent(name,value);
            return;
      }
   }
   function ProcessGadgetEvent(name, value)
   {
      _global.VxDebug("TabManager::ProcessGadgetEvent(): Passing to GadgetManager " + name + "," + value + "...");
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_RIGHT:
         case GUI.OSD_Components.TabManager.EVENT_LEFT:
         case GUI.OSD_Components.TabManager.EVENT_UP:
         case GUI.OSD_Components.TabManager.EVENT_DOWN:
         case GUI.OSD_Components.TabManager.EVENT_CW:
         case GUI.OSD_Components.TabManager.EVENT_CW_JUMP:
         case GUI.OSD_Components.TabManager.EVENT_CCW:
         case GUI.OSD_Components.TabManager.EVENT_CCW_JUMP:
         case GUI.OSD_Components.TabManager.EVENT_NE:
         case GUI.OSD_Components.TabManager.EVENT_SE:
         case GUI.OSD_Components.TabManager.EVENT_NW:
         case GUI.OSD_Components.TabManager.EVENT_SW:
            if(Number(value) > 0)
            {
               GUI.OSD_Components.GadgetManager.GetManager().onInputEvent(name,value);
            }
            return;
         default:
            GUI.OSD_Components.GadgetManager.GetManager().onInputEvent(name,value);
            return;
      }
   }
   function NavigateGizmoGrid(name, value)
   {
      var _loc4_;
      var _loc3_;
      if(value != "0")
      {
         _loc4_ = this.__targets.current()._parent._currentFrame;
         _global.VxDebug("TabManager::NavigateGizmoGrid(): " + name + "," + value + "            [Frame " + _loc4_ + "]");
         switch(name)
         {
            case GUI.OSD_Components.TabManager.EVENT_RIGHT:
               _loc3_ = this.__targets.right();
               break;
            case GUI.OSD_Components.TabManager.EVENT_LEFT:
               _loc3_ = this.__targets.left();
               break;
            case GUI.OSD_Components.TabManager.EVENT_UP:
               _loc3_ = this.__targets.up();
               break;
            case GUI.OSD_Components.TabManager.EVENT_DOWN:
               _loc3_ = this.__targets.down();
         }
         if(_loc3_ != null)
         {
            this.SetFocus(_loc3_);
         }
      }
   }
   function onKeyDown()
   {
      var _loc3_ = Key.getCode();
      if(this.__focused && this.__focused.onKeyDown)
      {
         this.__focused.onKeyDown();
      }
      var _loc2_;
      switch(_loc3_)
      {
         case 9:
            _loc2_ = !Key.isDown(16) ? this.__targets.next() : this.__targets.prev();
            break;
         case 39:
            _loc2_ = this.__targets.right();
            break;
         case 37:
            _loc2_ = this.__targets.left();
            break;
         case 38:
            _loc2_ = this.__targets.up();
            break;
         case 40:
            _loc2_ = this.__targets.down();
      }
      if(_loc2_ != null)
      {
         this.SetFocus(_loc2_);
      }
   }
   function onKeyUp()
   {
      if(this.__focused && this.__focused.onKeyUp)
      {
         this.__focused.onKeyUp();
      }
   }
   function SetFocus(target)
   {
      if(this.__focused && this.__focused.killFocus)
      {
         this.__focused.killFocus();
      }
      this.__focused = target;
      this.__targets.SetFocused(this.__focused != null);
      if(this.__focused && this.__focused.focus)
      {
         this.__focused.focus();
      }
   }
   function HasPrev()
   {
      return this.__targets.HasPrev();
   }
   function HasNext()
   {
      return this.__targets.HasNext();
   }
   function HasUp()
   {
      return this.__targets.HasUp();
   }
   function HasDown()
   {
      return this.__targets.HasDown();
   }
   function onSetFocus(oldTarget, newTarget)
   {
   }
   function push(targets)
   {
      if(targets instanceof Array)
      {
         targets = new GUI.OSD_Components.GizmoGrid(targets);
      }
      else if(targets.targetGrid instanceof Array)
      {
         targets = new GUI.OSD_Components.GizmoGrid(targets.targetGrid,targets.defaultFocusX,targets.defaultFocusY);
      }
      this.__targetStack.push(this.__targets);
      this.__targets = targets;
      if(this.__targets.isFocused())
      {
         this.SetFocus(this.__targets.current());
      }
      this.__targets.setVisible(true);
   }
   function pop()
   {
      var _loc3_ = false;
      this.__targets.setVisible(false);
      var _loc2_ = this.__targets;
      this.__targets = GUI.OSD_Components.GizmoGrid(this.__targetStack.pop());
      if(this.__targetStack.length == 0)
      {
         this.SetFocus(null);
         _loc3_ = true;
      }
      else if(this.__targets.isFocused())
      {
         this.SetFocus(this.__targets.current());
      }
      if(_loc2_ instanceof GUI.OSD_Components.GizmoGrid)
      {
         false;
      }
      return _loc3_;
   }
}
