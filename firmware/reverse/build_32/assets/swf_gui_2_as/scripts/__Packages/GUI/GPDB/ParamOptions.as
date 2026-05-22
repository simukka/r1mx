class GUI.GPDB.ParamOptions
{
   var __gpdb;
   var __param;
   var __selectedValue;
   var __selectedLabel;
   var __autoCommit;
   var __optionValues;
   var __optionSeries;
   var __lastUsedSeries;
   var __conditionalValues;
   var __maxValueParam;
   var __optionGeneratorParam;
   var __focusSeries;
   var __numOptions;
   var __focusChoices;
   var __optionMethod = "NONE";
   function ParamOptions(gpdb, param)
   {
      this.__gpdb = gpdb;
      this.__param = param;
      this.__selectedValue = "";
      this.__selectedLabel = "";
      this.__autoCommit = false;
      this.__optionValues = null;
      this.__optionSeries = null;
      this.__lastUsedSeries = this.__optionSeries;
      this.__conditionalValues = [];
   }
   function Commit()
   {
      _global.VxDebug("ParamOptions:Commit(" + this.__param.name + ", " + this.__selectedValue + ")");
      if(this.__selectedValue != undefined && this.__selectedValue != "")
      {
         this.__gpdb.paramSet(this.__param.name,this.__selectedValue);
         this.__param.label = this.__selectedLabel;
      }
   }
   function AutoCommit(enable)
   {
      this.__autoCommit = enable;
   }
   function isChanged()
   {
      return this.__selectedValue != this.__param.value;
   }
   function SetMaxValueParam(param)
   {
      _global.VxDebug("ParamOptions.SetMaxValueParam(\'" + param + "\') to limit \'" + this.__param.name + "\'");
      this.__maxValueParam = param;
   }
   function SetOptionGeneratorParam(param)
   {
      if(this.__optionMethod == "NONE")
      {
         this.__optionMethod = "ENUMERATED";
         this.__optionGeneratorParam = param;
         this.__gpdb.addCallbackWhenReady(param,mx.utils.Delegate.create(this,this.UpdateOptions));
      }
      else
      {
         _global.VxError("ParamOptions.SetOptionGeneratorParam(\'" + param + "\') Option-Mehtod already defined for \'" + this.__param.name + "\'");
      }
   }
   function UpdateOptions()
   {
      _global.VxDebug("ParamOptions:UpdateOptions(" + this.__param.name + ".options = f(" + this.__optionGeneratorParam + "))");
      this.SetAndCacheChoices();
   }
   function GrabListOfOptionsFromParam()
   {
      if(this.__optionGeneratorParam)
      {
         delete this.__optionValues;
         this.CreateOptionValues();
         var _loc12_ = this.__gpdb.paramGet(this.__optionGeneratorParam);
         if(_loc12_ != "")
         {
            var _loc10_ = _loc12_.split(";");
            var _loc11_ = _loc10_.length;
            var _loc13_ = Array();
            var _loc6_ = undefined;
            var _loc4_ = undefined;
            var _loc7_ = undefined;
            var _loc5_ = undefined;
            var _loc3_ = 0;
            while(_loc3_ < _loc11_)
            {
               _loc6_ = _loc10_[_loc3_];
               _loc4_ = _loc6_.split(",");
               if(_loc4_.length == 2)
               {
                  _loc7_ = this.StripLeadingWhiteSpace(_loc4_[0]);
                  _loc5_ = this.StripLeadingWhiteSpace(_loc4_[1]);
               }
               else
               {
                  _loc7_ = _loc5_ = this.StripLeadingWhiteSpace(_loc6_);
               }
               this.AddLegalValue({value:_loc7_,label:_loc5_});
               _loc3_ = _loc3_ + 1;
            }
         }
      }
      else
      {
         _global.VxError("ParamOptions::GrabListOfOptionsFromParam() No generating param was specified for " + this.__param.name);
      }
   }
   function SetAndCacheChoices()
   {
      var _loc3_ = undefined;
      var _loc5_ = undefined;
      if(this.__conditionalValues.length > 0)
      {
         this.__optionSeries = this.__optionValues = undefined;
         var _loc4_ = this.GetConditionalChoices();
         this.__optionSeries = _loc4_.getSeries();
         this.__optionValues = _loc4_.getValues();
         if(this.__optionSeries != undefined)
         {
            this.__optionMethod = "SERIES";
         }
         else if(this.__optionValues != undefined)
         {
            this.__optionMethod = "ENUMERATED";
         }
      }
      switch(this.__optionMethod)
      {
         case "SERIES":
            this.__focusSeries = this.GetBoundedSeries();
            this.__numOptions = Math.floor((this.__focusSeries.end - this.__focusSeries.start) / this.__focusSeries.increment) + 1;
            _loc5_ = this.SnapToSeries(Number(this.__param.value),this.__focusSeries);
            this.SetSelection(_loc5_);
            break;
         case "ENUMERATED":
            if(this.__optionGeneratorParam)
            {
               this.GrabListOfOptionsFromParam();
               _loc3_ = 0;
            }
            else
            {
               _loc3_ = this.IndexOfCurrentValue();
            }
            this.__focusChoices = this.GetBoundedValueList();
            this.__numOptions = this.__focusChoices.length;
            this.SetSelection(this.__optionValues.list[_loc3_].value,this.__optionValues.list[_loc3_].label);
            break;
         case "NONE":
         default:
            _global.VxError("ParamOptions::SetAndCacheChoices(" + this.__param.name + ") Not configured");
      }
   }
   function SnapToSeries(value, series)
   {
      var _loc1_ = undefined;
      if(value < series.start)
      {
         _loc1_ = series.start;
      }
      else if(value > series.end)
      {
         _loc1_ = series.end;
      }
      else
      {
         _loc1_ = value;
      }
      return _loc1_;
   }
   function SelectFirst()
   {
      switch(this.__optionMethod)
      {
         case "SERIES":
            this.SetSelection(this.__focusSeries.start);
            break;
         case "ENUMERATED":
            this.SetSelection(this.__focusChoices[0].value,this.__focusChoices[0].label);
      }
   }
   function SelectLast()
   {
      var _loc2_ = this.__focusChoices.length;
      switch(this.__optionMethod)
      {
         case "SERIES":
            this.SetSelection(this.__focusSeries.end);
            break;
         case "ENUMERATED":
            this.SetSelection(this.__focusChoices[_loc2_ - 1].value,this.__focusChoices[_loc2_ - 1].label);
      }
   }
   function SelectNext(step)
   {
      var _loc3_ = false;
      var _loc4_ = undefined;
      var _loc2_ = undefined;
      if(step == undefined || step < 1)
      {
         step = 1;
      }
      switch(this.__optionMethod)
      {
         case "SERIES":
            _loc4_ = Number(this.__selectedValue) + step * this.__focusSeries.increment;
            _loc3_ = _loc4_ <= this.__focusSeries.end;
            if(!_loc3_)
            {
               _loc4_ = this.__focusSeries.end;
            }
            this.SetSelection(_loc4_);
            break;
         case "ENUMERATED":
            _loc2_ = this.__optionValues.indexMap[this.__selectedValue];
            if(_loc2_ != undefined)
            {
               _loc2_ += step;
               var _loc5_ = this.__focusChoices.length;
               _loc3_ = _loc2_ < _loc5_;
               if(_loc3_)
               {
                  this.SetSelection(this.__focusChoices[_loc2_].value,this.__focusChoices[_loc2_].label);
               }
               else
               {
                  this.SetSelection(this.__focusChoices[_loc5_ - 1].value,this.__focusChoices[_loc5_ - 1].label);
               }
            }
      }
      return _loc3_;
   }
   function SelectPrev(step)
   {
      var _loc3_ = false;
      var _loc4_ = undefined;
      var _loc2_ = undefined;
      if(step == undefined || step < 1)
      {
         step = 1;
      }
      switch(this.__optionMethod)
      {
         case "SERIES":
            _loc4_ = Number(this.__selectedValue) - step * this.__focusSeries.increment;
            _loc3_ = _loc4_ >= this.__focusSeries.start;
            if(!_loc3_)
            {
               _loc4_ = this.__focusSeries.start;
            }
            this.SetSelection(_loc4_);
            break;
         case "ENUMERATED":
            _loc2_ = this.__optionValues.indexMap[this.__selectedValue];
            if(_loc2_ != undefined)
            {
               _loc2_ -= step;
               _loc3_ = _loc2_ >= 0;
               if(_loc3_)
               {
                  this.SetSelection(this.__focusChoices[_loc2_].value,this.__focusChoices[_loc2_].label);
               }
               else
               {
                  this.SetSelection(this.__focusChoices[0].value,this.__focusChoices[0].label);
               }
            }
      }
      return _loc3_;
   }
   function SetSelection(value, label)
   {
      if(label == undefined)
      {
         if(this.__optionMethod == "SERIES" && this.__param.type == "float")
         {
            var _loc4_ = this.DecimalPlaces(this.__focusSeries.increment.toString());
            label = this.FormatDecimals(value,_loc4_);
         }
         else
         {
            label = value;
         }
      }
      this.__selectedValue = value;
      this.__selectedLabel = label;
      if(this.__autoCommit)
      {
         this.Commit();
      }
   }
   function GetSelectionLabel()
   {
      return this.__selectedLabel;
   }
   function GetSelectionValue()
   {
      return this.__selectedValue;
   }
   function AddLegalValue(itemObj)
   {
      if(this.__optionMethod == "NONE")
      {
         this.__optionMethod = "ENUMERATED";
      }
      if(this.__optionMethod == "ENUMERATED")
      {
         if(this.__optionValues == undefined)
         {
            this.CreateOptionValues();
         }
         var _loc3_ = 0;
         while(_loc3_ < this.__optionValues.list.length)
         {
            if(this.__optionValues.list[_loc3_].value == itemObj.value)
            {
               return undefined;
            }
            _loc3_ = _loc3_ + 1;
         }
         itemObj.index = this.__optionValues.list.length;
         this.__optionValues.list.push(itemObj);
         this.__optionValues.indexMap[itemObj.value] = itemObj.index;
      }
      else
      {
         _global.VxError("ParamOptions:AddLegalValue(): Option-Methed not compatible. " + this.__optionMethod);
      }
   }
   function CreateOptionValues()
   {
      this.__optionValues = new Object();
      this.__optionValues.list = [];
      this.__optionValues.indexMap = [];
   }
   function GetBoundedValueList()
   {
      var _loc3_ = this.__optionValues.list;
      if(this.__maxValueParam)
      {
         var _loc4_ = this.__gpdb.paramGetNumber(this.__maxValueParam);
         if(_loc4_ < _loc3_[_loc3_.length - 1])
         {
            var _loc2_ = undefined;
            do
            {
               _loc2_ = _loc3_.pop();
            }
            while(_loc2_.value > _loc4_);
            
            _loc3_.push(_loc2_);
         }
      }
      return _loc3_;
   }
   function set series(series)
   {
      if(this.__optionMethod == "NONE")
      {
         this.__optionMethod = "SERIES";
      }
      if(this.__optionMethod == "SERIES")
      {
         this.__optionSeries = series;
         this.__lastUsedSeries = this.__optionSeries;
      }
      else
      {
         _global.VxError("ParamOptions:set.series(): incompatible option-method: " + this.__optionMethod);
      }
   }
   function GetBoundedSeries()
   {
      if(this.__maxValueParam)
      {
         var _loc2_ = this.__gpdb.paramGetNumber(this.__maxValueParam);
         if(_loc2_ < this.__optionSeries.end)
         {
            var _loc5_ = this.__optionSeries.end - _loc2_;
            var _loc4_ = Math.floor(_loc5_ / this.__optionSeries.increment);
            var _loc3_ = this.__optionSeries.end - _loc4_ * this.__optionSeries.increment;
            this.__optionSeries.end = _loc3_;
         }
      }
      return this.__optionSeries;
   }
   function NumOptions()
   {
      return this.__numOptions;
   }
   function SetConditionalValues(values)
   {
      this.__conditionalValues = values;
   }
   function GetConditionalChoices()
   {
      var _loc4_ = undefined;
      _global.VxDebug("ParamOptions::GetConditionalChoices() for " + this.__param.name);
      var _loc3_ = 0;
      while(_loc3_ < this.__conditionalValues.length)
      {
         if(this.__conditionalValues[_loc3_].IsSatisfied())
         {
            _loc4_ = this.__conditionalValues[_loc3_].copy();
            break;
         }
         _loc3_ = _loc3_ + 1;
      }
      return _loc4_;
   }
   function IndexOfCurrentValue()
   {
      return this.IndexOfValue(this.__param.value);
   }
   function IndexOfSelectedValue()
   {
      return this.IndexOfValue(this.__selectedValue);
   }
   function IndexOfValue(value)
   {
      var _loc3_ = 0;
      switch(this.__optionMethod)
      {
         case "SERIES":
            _loc3_ = Math.round((value - this.__optionSeries.start) / this.__optionSeries.increment);
            break;
         case "ENUMERATED":
            _loc3_ = this.__optionValues.indexMap[value];
            break;
         default:
            _global.VxError("ParamOptions::IndexOfValue() invalid option-method: " + this.__optionMethod);
      }
      return _loc3_;
   }
   function FormatDecimals(num, digits)
   {
      var _loc4_ = undefined;
      if(digits <= 0)
      {
         _loc4_ = Math.round(num).toString();
      }
      else
      {
         var _loc5_ = Math.pow(10,digits);
         var _loc2_ = String(Math.round(num * _loc5_) / _loc5_);
         if(_loc2_.indexOf(".") == -1)
         {
            _loc2_ += ".0";
         }
         var _loc7_ = _loc2_.split(".");
         var _loc3_ = digits - _loc7_[1].length;
         var _loc1_ = 1;
         while(_loc1_ <= _loc3_)
         {
            _loc2_ += "0";
            _loc1_ = _loc1_ + 1;
         }
         _loc4_ = _loc2_;
      }
      return _loc4_;
   }
   function GetExpandedChoice(value)
   {
      if(value == undefined)
      {
         _global.VxError("GPdbParam:GetExpandedChoice() value is \'undefined\'");
      }
      if(this.__lastUsedSeries)
      {
         var _loc4_ = this.DecimalPlaces(this.__lastUsedSeries.increment.toString());
         value = this.FormatDecimals(Number(value),_loc4_);
      }
      return value;
   }
   function DecimalPlaces(n)
   {
      var _loc1_ = 0;
      var _loc2_ = n.indexOf(".");
      if(_loc2_ > -1)
      {
         _loc1_ = n.length - _loc2_ - 1;
      }
      return _loc1_;
   }
   function StripLeadingWhiteSpace(s)
   {
      var _loc1_ = 0;
      while(s.charAt(_loc1_) == " ")
      {
         _loc1_ = _loc1_ + 1;
      }
      if(_loc1_ == 0)
      {
         return s;
      }
      return s.substr(_loc1_);
   }
}
