class GUI.OSD_Components.ListController extends GUI.OSD_Components.Gadget
{
   var __gpdb;
   var __options;
   var __prefix;
   var __suffix;
   var __selectedIndex;
   var __entryIndex;
   var __selectedLabel;
   var __positionBar;
   var __commitHandler;
   var __managedParam;
   var __maxValueParam;
   var __jumpSize;
   var __isDynamicList = false;
   var __continuousUpdate = false;
   var INDICATOR_STATE_UP = 1;
   var INDICATOR_STATE_DOWN = 2;
   var INDICATOR_STATE_DISABLED = 3;
   function ListController()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__options = new Array();
      this.__prefix = this.__suffix = "";
      this.__selectedIndex = 0;
      this.__entryIndex = null;
      if(this.__selectedLabel == undefined)
      {
         _global.VxError("ListController::CTOR() \'__selectedLabel\' *must* be specified for creation");
         throw new Error("EXCEPTION: ListController::CTOR() \'__selectedLabel\' *must* be specified for creation");
      }
      if(this.__positionBar == undefined)
      {
         _global.VxError("ListController::CTOR() \'__positionBar\' *must* be specified for creation");
         throw new Error("EXCEPTION: ListController::CTOR() \'__positionBar\' *must* be specified for creation");
      }
      this.focusEnabled = true;
   }
   function SetCommitHandler(fnc, paramName)
   {
      this.__commitHandler = fnc;
      this.__managedParam = paramName;
   }
   function GetValue()
   {
      var _loc2_ = undefined;
      if(this.__options && this.__options.length > 0)
      {
         _loc2_ = this.__options[this.__selectedIndex].value;
         return _loc2_;
      }
      throw new Error("EXCEPTION: ListController::GetValue() no __options array for \'" + this.__managedParam + "\'");
   }
   function GetText()
   {
      var _loc2_ = undefined;
      if(this.__options && this.__options.length > 0)
      {
         _loc2_ = this.__prefix + this.__options[this.__selectedIndex].label + this.__suffix;
         return _loc2_ == undefined ? "None Available" : _loc2_;
      }
      throw new Error("EXCEPTION: ListController::GetText() no __options array for \'" + this.__managedParam + "\'");
   }
   function SetOptionsList(options, entryValue, isDynamicList)
   {
      if(options == undefined)
      {
         _global.VxDebug("ListController::SetOptionsList() \'options\' array UNDEFINED for \'" + this.__managedParam + "\'");
      }
      else if(options.length == 0)
      {
         _global.VxDebug("ListController::SetOptionsList() EMPTY \'options\' array for \'" + this.__managedParam + "\'");
      }
      else
      {
         if(entryValue == undefined)
         {
            _global.VxError("ListController:SetOptionsList() of \'" + this.__managedParam + " is \'undefined\'");
         }
         _global.VxLog("ListController:SetEntryValue(\'" + entryValue + "\'): {" + this.__options + "}");
         this.SetOptions(options);
         this.SetEntryValue(entryValue);
      }
      this.__isDynamicList = isDynamicList;
   }
   function SetOptions(options)
   {
      var _loc7_ = new Array();
      if(options[0].value == undefined)
      {
         var _loc2_ = 0;
         while(_loc2_ < options.length)
         {
            var _loc3_ = options[_loc2_];
            _loc7_.push({value:_loc3_,label:_loc3_});
            _loc2_ = _loc2_ + 1;
         }
         this.__options = _loc7_;
      }
      else
      {
         this.__options = options;
      }
      this.__entryIndex = this.__selectedIndex;
   }
   function SetEntryValue(entryValue)
   {
      if(entryValue == undefined)
      {
         _global.VxError("ListController:SetEntryValue() of \'" + this.__managedParam + " is \'undefined\'");
      }
      else if(this.__options == undefined)
      {
         _global.VxError("ListController:SetEntryValue(\'" + entryValue + "\') no options list");
      }
      else
      {
         var _loc4_ = this.BoundMaxValue(entryValue);
         _global.VxLog("ListController:SetEntryValue() configuring positionBar...   <------------------------------");
         this.__positionBar.SetLength(this.__options.length);
         this.__positionBar.SetMarkerIndex(this.__entryIndex);
         this.calculateJumpSize();
      }
   }
   function BoundMaxValue(entryValue)
   {
      if(entryValue == undefined)
      {
         _global.VxError("ListController::BoundMaxValue() of \'undefined\' value.");
      }
      else if(this.__maxValueParam != undefined)
      {
         if(this.__options == undefined)
         {
            _global.VxError("ListController::BoundMaxValue() of \'" + this.__managedParam + "\' undefined __options array. Ignoring.");
         }
         else if(this.__options.length == 0)
         {
            _global.VxError("ListController::BoundMaxValue() \'" + this.__managedParam + "\' empty __options array. Ignoring.");
         }
         else
         {
            var _loc9_ = undefined;
            var _loc8_ = this.__gpdb.paramGetNumber(this.__maxValueParam);
            var _loc7_ = this.NumValuesInBounds();
            this.__options = this.__options.slice(0,_loc7_);
            if(Number(entryValue) > _loc8_)
            {
               entryValue = this.__options[_loc7_ - 1].value;
            }
         }
      }
      if(this.__options != undefined && this.__options.length > 0)
      {
         var _loc6_ = false;
         var _loc5_ = 0;
         var _loc3_ = 0;
         while(_loc3_ < this.__options.length)
         {
            if(this.__options[_loc3_].value == entryValue)
            {
               _loc5_ = Number(_loc3_);
               _loc6_ = true;
               break;
            }
            _loc3_ = _loc3_ + 1;
         }
         if(_loc6_)
         {
            this.__selectedIndex = this.__entryIndex = _loc5_;
         }
         else
         {
            _global.VxError("ListController:BoundMaxValue(\'" + entryValue + "\') value not in options list of \'" + this.__managedParam + "\'");
            _loc3_ = 0;
            while(_loc3_ < options.length)
            {
               _global.VxError("   __options[" + _loc3_ + "]: " + this.__options[_loc3_].value);
               _loc3_ = _loc3_ + 1;
            }
         }
      }
      return entryValue;
   }
   function setPrefix(prefix)
   {
      this.__prefix = prefix;
   }
   function setSuffix(suffix)
   {
      this.__suffix = suffix;
   }
   function setContinuousUpdate(continuousUpdate)
   {
      this.__continuousUpdate = continuousUpdate;
   }
   function setMaxValueParam(param)
   {
      var _loc4_ = this.__gpdb.paramType(param);
      if(_loc4_ == "integer" || _loc4_ == "float")
      {
         _global.VxDebug("::ListController.setMaxValueParam(\'" + param + "\') to limit \'" + this.__managedParam + "\'");
         this.__maxValueParam = param;
      }
      throw new Error("EXCEPTION: ListController::setMaxValueParam() \'" + param + "\' must be of type \'float\' or \'integer\'");
   }
   function calculateJumpSize()
   {
      this.__jumpSize = Math.floor(this.__options.length / 4);
      if(this.__jumpSize < 1)
      {
         this.__jumpSize = 1;
      }
   }
   function isChanged()
   {
      return this.__selectedIndex != this.__entryIndex;
   }
   function selectNext(jump)
   {
      if(this.__selectedIndex < this.__options.length - 1)
      {
         var _loc2_ = this.__selectedIndex + jump;
         if(_loc2_ > this.__options.length - 1)
         {
            _loc2_ = this.__options.length - 1;
         }
         this.__selectedIndex = _loc2_;
         this.Paint();
         this.onChange();
      }
   }
   function selectPrev(jump)
   {
      if(this.__selectedIndex > 0)
      {
         var _loc2_ = this.__selectedIndex - jump;
         if(_loc2_ < 0)
         {
            _loc2_ = 0;
         }
         this.__selectedIndex = _loc2_;
         this.Paint();
         this.onChange();
      }
   }
   function jumpForward()
   {
      this.selectNext(this.__jumpSize);
   }
   function jumpBack()
   {
      this.selectPrev(this.__jumpSize);
   }
   function Paint()
   {
      this.__selectedLabel.text = this.GetText();
      this.__positionBar.SetIndex(this.__selectedIndex);
      this.__positionBar.Paint();
      this.UpdateStatusLCD();
   }
   function NumValuesInBounds()
   {
      var _loc5_ = 0;
      var _loc4_ = this.__options;
      var _loc6_ = this.__gpdb.paramGetNumber(this.__maxValueParam);
      _global.VxDebug("ListController::NumValuesInBounds() num elements: " + _loc4_.length + ", maxVal " + _loc6_ + ", parameter \'" + this.__managedParam + "\'");
      if(_loc4_.length > 0)
      {
         var _loc3_ = 0;
         while(_loc3_ < _loc4_.length)
         {
            if(Number(_loc4_[_loc3_].value) > _loc6_)
            {
               break;
            }
            _loc5_ = _loc3_ + 1;
            _loc3_ = _loc3_ + 1;
         }
         if(_loc5_ == 0)
         {
            _global.VxError("ListController::NumValuesInBounds() bounding parameter precludes ALL values for \'" + this.__managedParam + "\'!");
            _loc5_ = 1;
         }
         else
         {
            _global.VxDebug("ListController::NumValuesInBounds() Limiting selector of \'" + this.__managedParam + "\' to " + _loc5_ + " of " + this.__options.length + ": ");
         }
      }
      else
      {
         _global.VxError("ListController::NumValuesInBounds() empty options array for \'" + this.__managedParam + "\'!");
      }
      return _loc5_;
   }
   function DEBUG_ShowOptions(first, num)
   {
      if(first == undefined)
      {
         first = 0;
         last = this.__options.length;
      }
      i = first;
      while(i < num)
      {
         _global.VxDebug("   label:" + this.__options[i].label + ", value:" + this.__options[i].value);
         i++;
      }
   }
   function UpdateStatusLCD()
   {
      var _loc2_ = this.GetText();
      GUI.OSD_Components.StatusLCD.GetManager().SetSelectValue(_loc2_);
   }
   function onChange()
   {
      if(this.__continuousUpdate)
      {
         this.onCommit();
      }
      if(this.__entryIndex != this.__selectedIndex)
      {
      }
   }
   function onCommit()
   {
      if(this.__isDynamicList || this.__entryIndex != this.__selectedIndex)
      {
         this.__entryIndex = this.__selectedIndex;
         _global.VxDebug("ListController::onCommit() setting to \'" + this.GetValue() + "\' for \'" + this.__managedParam + "\'");
         this.__commitHandler(this.GetValue());
         this.__positionBar.SetMarkerIndex(this.__entryIndex);
      }
   }
   function onUndo()
   {
      this.__selectedIndex = this.__entryIndex;
      this.__positionBar.SetMarkerIndex(this.__entryIndex);
      this.Paint();
   }
   function onKeyUp()
   {
      var _loc0_ = null;
      if((_loc0_ = Key.getCode()) === 13)
      {
         this.onCommit();
      }
   }
   function onKeyDown()
   {
      switch(Key.getCode())
      {
         case 34:
            this.jumpForward();
            break;
         case 33:
            this.jumpBack();
            break;
         case 39:
            this.selectNext(1);
            break;
         case 37:
            this.selectPrev(1);
      }
   }
   function onInputEvent(name, value)
   {
      var _loc2_ = Number(value);
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_UNDO:
            this.onUndo();
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW_JUMP:
            if(_loc2_ > 0)
            {
               this.jumpForward();
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW_JUMP:
            if(_loc2_ > 0)
            {
               this.jumpBack();
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW:
            if(_loc2_ > 0)
            {
               this.selectNext(_loc2_);
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW:
            if(_loc2_ > 0)
            {
               this.selectPrev(_loc2_);
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_SELECT:
            if(value == "false")
            {
               this.onCommit();
            }
      }
   }
}
