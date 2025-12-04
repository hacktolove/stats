/*********************************************************************
* @function      : tafqeet(Number, ISO_code, [{options}])
* @purpose       : Converts Currency Values to Full Arabic Words
* @version       : 2.00
* @author        : Mohsen Alyafei
* @date          : 04 March 2022
* @Licence       : MIT
* @param         : {Number} Numeric (required)
* @param         : {code} 3-letter ISO Currency Code
* @param         : [{options}] 3 Options passed as object {name:value} as follows:
*                  {comma:'on'}      : Insert comma between triplet words.
*                  {legal: 'on'}     : Uses legal mode
*                  {format: 'short'} : Uses fractions for any decimal part.
* @returns       : {string} The wordified number string in Arabic.
*
**********************************************************************/
function tafqeet(numIn=0, code, op={}){
    let iso=tafqeetISOList[code];if(!iso)throw new Error("Currency code not in the list!");
    let arr=(numIn+="").split((0.1).toLocaleString().substring(1,2)),
    out=nToW(arr[0],iso.uGender=="female",op,[iso.uSingle,iso.uDouble,iso.uPlural]),
    frc=arr[1]?(arr[1]+"000").substring(0,iso.fraction):0;
    if (frc !=0){out+="، و"+(op.format=="short"?frc+"/1"+"0".repeat(+iso.fraction)+" "+iso.uSingle:
    nToW(frc,iso.sGender=="female",op,[iso.sSingle,iso.sDouble,iso.sPlural]));}
    return out;
    
    function nToW(numIn=0,fm,{comma,legal}={},names){
    if(numIn==0)return"صفر "+iso.uSingle;
    let tS=[,"ألف","مليون","مليار","ترليون","كوادرليون","كوينتليون","سكستليون"],tM=["","واحد","اثنان","ثلاثة","أربعة","خمسة","ستة","سبعة","ثمانية","تسعة","عشرة"],tF=["","واحدة","اثنتان","ثلاث","أربع","خمس","ست","سبع","ثمان","تسع","عشر"],
    num=(numIn+=""),tU=[...tM],t11=[...tM],out="",n99,SpWa=" و",miah="مائة",
    last=~~(((numIn="0".repeat(numIn.length*2%3)+numIn).replace(/0+$/g,"").length+2)/3)-1;
    t11[0]="عشر";t11[1]="أحد";t11[2]="اثنا";
    numIn.match(/.{3}/g).forEach((n,i)=>+n&&(out+=do999(numIn.length/3-i-1,n,i==last),i!==last&&(out+=(comma=='on'?"،":"")+SpWa)));
    let sub=" "+names[0],n=+(num+"").slice(-2);if(n>10)sub=" "+tanween(names[0]);else if(n>2)sub=" "+names[2];
    else if(n>0)sub=names[n-1]+" "+(fm?tF[n]:tM[n]);
    return out+sub;
    
    function tanween(n,a=n.split` `,L=a.length-1){
    const strTF=(str,l=str.slice(-1),o=str+"ًا")=>{return"ا"==l?o=str.slice(0,-1)+"ًا":"ة"==l&&(o=str+"ً"),o;};
    for(let i=0;i<=L;i++)if(!i||i==L)a[i]=strTF(a[i]);return a.join` `;}
    
    function do999(sPos,num,last){
    let scale=tS[sPos],n100=~~(num/100),nU=(n99=num%100)%10,n10=~~(n99/10),w100="",w99="",e8=(nU==8&&fm&&!scale)?"ي":"";
    if (fm&&!scale){[tU,t11,t11[0],t11[1],t11[2]]=[[...tF],[...tF],"عشرة","إحدى","اثنتا"];if(n99>20)tU[1]="إحدى";}
    if(n100){if(n100>2)w100=tF[n100]+miah;else if(n100==1)w100=miah;else w100=miah.slice(0,-1)+(!n99||legal=="on"?"تا":"تان");}
    if(n99>19)w99=tU[nU]+(nU?SpWa:"")+(n10==2?"عشر":tF[n10])+"ون";
    else if(n99>10)w99=t11[nU]+e8+" "+t11[0];else if(n99>2)w99=tU[n99]+e8;let nW=w100+(n100 && n99?SpWa:"")+w99;
    if(!scale)return nW;if(!n99)return nW+" "+scale;if(n99>2)return nW+" "+(n99>10?scale+(last?"":"ًا")
    :(sPos<3?[,"آلاف","ملايين"][sPos]:tS[sPos]+"ات"));nW=(n100?w100+((legal=="on"&&n99<3)?" "+scale:"")+SpWa:"")+scale;
    return(n99==1)?nW:nW+(last?"ا":"ان");}}}
    //=====================================================================
    
    
    
    
    
    
    
    //==================== Common ISO Currency List in Arabic ===============
    let tafqeetISOList={
    AED:{uSingle :"درهم إماراتي",uDouble:"درهمان إماراتيان",uPlural:"دراهم إماراتية",uGender:"male",
     sSingle :"فلس",sDouble:"فلسان",sPlural:"فلوس",sGender:"male",fraction:2},
    
    BHD:{uSingle :"دينار بحريني",uDouble:"ديناران بحرينيان",uPlural:"دنانير بحرينية",uGender:"male",
     sSingle :"فلس",sDouble:"فلسان",sPlural:"فلوس",sGender:"male",fraction:3},
    
    EGP:{uSingle :"جنيه مصري",uDouble:"جنيهان مصريان",uPlural:"جنيهات مصرية",uGender:"male",
     sSingle :"قرش",sDouble:"قرشان",sPlural:"قروش",sGender:"male",fraction:2},
    
    EUR:{uSingle :"يورو",uDouble:"يوروان",uPlural:"يوروات",uGender:"male",
     sSingle:"سنت",sDouble:"سنتان",sPlural:"سنتات",sGender:"male",fraction:2},
    
    GBP:{uSingle :"جنيه إسترليني",uDouble:"جنيهان إسترلينيان",uPlural:"جنيهات إسترلينية",uGender:"male",
     sSingle :"بنس",sDouble:"بنسان",sPlural:"بنسات",sGender:"male",fraction:2},
    
    INR:{uSingle :"روبية هندية",uDouble:"روبيتان هنديتان",uPlural:"روبيات هندية",uGender:"female",
     sSingle :"بيسة",sDouble:"بيستان",sPlural:"بيسات",sGender:"female",fraction:2},
    
    IQD:{uSingle :"دينار عراقي",uDouble:"ديناران عراقيان",uPlural:"دنانير عراقية",uGender:"male",
     sSingle :"فلس",sDouble:"فلسان",sPlural:"فلوس",sGender:"male",fraction:2},
    
    JOD:{uSingle :"دينار أردني",uDouble:"ديناران أردنيان",uPlural:"دنانير أردنية",uGender:"male",
     sSingle :"فلس",sDouble:"فلسان",sPlural:"فلوس",sGender:"male",fraction:3},
    
    KWD:{uSingle :"دينار كويتي",uDouble:"ديناران كويتيان",uPlural:"دنانير كويتية",uGender:"male",
     sSingle :"فلس",sDouble:"فلسان",sPlural:"فلوس",sGender:"male",fraction:3},
    
    LBP:{uSingle :"ليرة لبنانية",uDouble:"ليرتان لبنانيتان",uPlural :"ليرات لبنانية",uGender:"female",
     sSingle :"قرش",sDouble:"قرشان",sPlural:"قروش",sGender:"male",fraction:2},
    
    LYD:{uSingle :"دينار ليبي",uDouble:"ديناران ليبيان",uPlural:"دنانير ليبية",uGender:"male",
     sSingle:"درهم",sDouble:"درهمان",sPlural: "دراهم",sGender:"male",fraction:3},
    
    MAD:{uSingle :"درهم مغربي",uDouble:"درهمان مغربيان",uPlural:"دراهم مغربية",uGender:"male",
     sSingle :"سنتيم",sDouble:"سنتيمان",sPlural:"سنتيمات",sGender:"male",fraction:2},
    
    OMR:{uSingle :"ريال عماني",uDouble:"ريالان عمانيان",uPlural:"ريالات عمانية",uGender:"male",
     sSingle :"بيسة",sDouble:"بيستان",sPlural:"بيسات",sGender:"female",fraction:3},
    
    QAR:{uSingle:"ريال قطري",uDouble:"ريالان قطريان",uPlural:"ريالات قطرية",uGender:"male",
     sSingle:"درهم",sDouble:"درهمان",sPlural: "دراهم",sGender:"male",fraction:2},
    
    SAR:{uSingle:"ريال سعودي",uDouble:"ريالان سعوديان",uPlural:"ريالات سعودية",uGender:"male",
     sSingle:"هللة",sDouble:"هللتان",sPlural: "هللات",sGender:"female",fraction:2},
    
    SDG:{uSingle :"جنيه سوداني",uDouble:"جنيهان سودانيان",uPlural:"جنيهات سودانية",uGender:"male",
     sSingle :"قرش",sDouble:"قرشان",sPlural:"قروش",sGender:"male",fraction:2},
    
    SOS:{uSingle :"شلن صومالي",uDouble:"شلنان صوماليان",uPlural:"شلنات صومالية",uGender:"male",
     sSingle:"سنت",sDouble:"سنتان",sPlural:"سنتات",sGender:"male",fraction:2},
    
    SSP:{uSingle :"جنيه جنوب سوداني",uDouble:"جنيهان جنوب سودانيان",uPlural:"جنيهات جنوب سودانية",uGender:"male",
     sSingle :"قرش",sDouble:"قرشان",sPlural:"قروش",sGender:"male",fraction:2},
    
    SYP:{uSingle :"ليرة سورية",uDouble:"ليرتان سوريتان",uPlural :"ليرات سورية",uGender:"female",
     sSingle :"قرش",sDouble:"قرشان",sPlural:"قروش",sGender:"male",fraction:2},
    
    TND:{uSingle :"دينار تونسي",uDouble:"ديناران تونسيان",uPlural:"دنانير تونسية",uGender:"male",
     sSingle :"مليم",sDouble:"مليمان",sPlural:"ملاليم",sGender:"male",fraction:3},
    
    USD:{uSingle:"دولار أمريكي",uDouble:"دولاران أمريكيان",uPlural:"دولارات أمريكية",uGender:"male",
     sSingle:"سنت",sDouble:"سنتان",sPlural:"سنتات",sGender:"male",fraction:2},
    
    YER:{uSingle:"ريال يمني",uDouble:"ريالان يمنيان",uPlural:"ريالات يمنية",uGender:"male",
     sSingle:"فلس",sDouble:"فلسان",sPlural: "فلوس",sGender:"male",fraction:2},
    
    //==== add here
    
    }; // end of list
    
    //***********************************************
    
    
    
    
    
    
    
    
    
    
    // //========================
    // var r=0; // test tracker
    // //===============
    // r |= test(1,"QAR",{},"ريال قطري واحد");
    // r |= test(1.01,"QAR",{},"ريال قطري واحد، ودرهم واحد");
    // r |= test(0.02,"QAR",{},"صفر ريال قطري، ودرهمان اثنان");
    // r |= test(2.08,"QAR",{},"ريالان قطريان اثنان، وثمانية دراهم");
    // r |= test(2.03,"QAR",{},"ريالان قطريان اثنان، وثلاثة دراهم");
    // r |= test(2.25,"QAR",{},"ريالان قطريان اثنان، وخمسة وعشرون درهمًا");
    // r |= test(21.18,"QAR",{},"واحد وعشرون ريالًا قطريًا، وثمانية عشر درهمًا");
    // r |= test(221.21,"QAR",{},"مائتان وواحد وعشرون ريالًا قطريًا، وواحد وعشرون درهمًا");
    // r |= test(200.21,"QAR",{},"مائتا ريال قطري، وواحد وعشرون درهمًا");
    // r |= test(2000.15,"QAR",{},"ألفا ريال قطري، وخمسة عشر درهمًا");
    // r |= test(21022.38,"QAR",{},"واحد وعشرون ألفًا واثنان وعشرون ريالًا قطريًا، وثمانية وثلاثون درهمًا");
    // r |= test(200000.38,"QAR",{},"مائتا ألف ريال قطري، وثمانية وثلاثون درهمًا");
    // r |= test(2000000.123,"QAR",{},"مليونا ريال قطري، واثنا عشر درهمًا");
    
    // if (r==0) console.log("✅ Test Cases - Male Currency & Male Sub-Currency   ....Passed.");
    
    // //========================
    // r |= test(1,"LBP",{},"ليرة لبنانية واحدة");
    // r |= test(1.01,"LBP",{},"ليرة لبنانية واحدة، وقرش واحد");
    // r |= test(0.02,"LBP",{},"صفر ليرة لبنانية، وقرشان اثنان");
    // r |= test(2.08,"LBP",{},"ليرتان لبنانيتان اثنتان، وثمانية قروش");
    // r |= test(2.03,"LBP",{},"ليرتان لبنانيتان اثنتان، وثلاثة قروش");
    // r |= test(2.25,"LBP",{},"ليرتان لبنانيتان اثنتان، وخمسة وعشرون قرشًا");
    // r |= test(21.18,"LBP",{},"إحدى وعشرون ليرةً لبنانيةً، وثمانية عشر قرشًا");
    // r |= test(221.21,"LBP",{},"مائتان وإحدى وعشرون ليرةً لبنانيةً، وواحد وعشرون قرشًا");
    // r |= test(200.21,"LBP",{},"مائتا ليرة لبنانية، وواحد وعشرون قرشًا");
    // r |= test(2000.15,"LBP",{},"ألفا ليرة لبنانية، وخمسة عشر قرشًا");
    // r |= test(21022.38,"LBP",{},"واحد وعشرون ألفًا واثنتان وعشرون ليرةً لبنانيةً، وثمانية وثلاثون قرشًا");
    // r |= test(200000.38,"LBP",{},"مائتا ألف ليرة لبنانية، وثمانية وثلاثون قرشًا");
    // r |= test(2000000.123,"LBP",{},"مليونا ليرة لبنانية، واثنا عشر قرشًا");
    
    // if (r==0) console.log("✅ Test Cases - Female Currency & Male Sub-Currency   ....Passed.");
    
    // //========================
    // r |= test(1,"OMR",{},"ريال عماني واحد");
    // r |= test(1.01,"OMR",{},"ريال عماني واحد، وعشر بيسات");
    // r |= test(0.02,"OMR",{},"صفر ريال عماني، وعشرون بيسةً");
    // r |= test(2.08,"OMR",{},"ريالان عمانيان اثنان، وثمانون بيسةً");
    // r |= test(2.03,"OMR",{},"ريالان عمانيان اثنان، وثلاثون بيسةً");
    // r |= test(2.25,"OMR",{},"ريالان عمانيان اثنان، ومائتان وخمسون بيسةً");
    // r |= test(21.18,"OMR",{},"واحد وعشرون ريالًا عمانيًا، ومائة وثمانون بيسةً");
    // r |= test(221.21,"OMR",{},"مائتان وواحد وعشرون ريالًا عمانيًا، ومائتان وعشر بيسات");
    // r |= test(200.21,"OMR",{},"مائتا ريال عماني، ومائتان وعشر بيسات");
    // r |= test(2000.15,"OMR",{},"ألفا ريال عماني، ومائة وخمسون بيسةً");
    // r |= test(21022.38,"OMR",{},"واحد وعشرون ألفًا واثنان وعشرون ريالًا عمانيًا، وثلاثمائة وثمانون بيسةً");
    // r |= test(200000.38,"OMR",{},"مائتا ألف ريال عماني، وثلاثمائة وثمانون بيسةً");
    // r |= test(2000000.123,"OMR",{},"مليونا ريال عماني، ومائة وثلاث وعشرون بيسةً");
    
    // if (r==0) console.log("✅ Test Cases - Male Currency & Female Sub-Currency   ....Passed.");
    
    
    // //------------------
    // function test(n,code,options,should) {
    // let result = tafqeet(n,code,options);
    // if (result !== should) {console.log(`${n} Output   : ${result}\n${n} Should be: ${should}`);return 1;}
    // }

    frappe.tafqeet = tafqeet