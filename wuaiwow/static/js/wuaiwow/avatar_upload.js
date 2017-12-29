$.avatarUpload=new function(){
	var g_filepath="";
	var g_error={
		413:{msg:"请确保文件小于300KB",css:"msg_err"},
		401:{msg:"登陆超时",css:"msg_err"},
		200:{msg:"成功",css:"msg_ok"},
		503:{msg:"打开文件错误",css:"msg_err"},
		504:{msg:"图片转换错误",css:"msg_err"}
	};

	var g_allow_suffix={
		jpg:true,jpeg:true,png:true
	};
	this.imgSelector=undefined;
	function showMsg(msg,type){
		var css=type||"msg_err";
		$("#avatar_result").fadeOut(500,function(){
			$("#avatar_result").attr("class",css);
			$("#avatar_result").html(msg);
			$(this).fadeIn(500);
		});
	}
	function showResultMsg(msg,data)
	{
			var css="msg_err";
			if(data){
				var def=g_error[data.result]
				if(def){
					msg=msg+def.msg;
					css=def.css;
				}
			}
			showMsg(msg,css);
	}
	function getFileName(filepath){
		var filename=filepath.match(/[/\\]([^\s/\\]+)\.(\w+)$/);
		if(!filename)
			filename=filepath.match(/^([^\s/\\]+)\.(\w+)$/);
		return filename;
	}

	function getAllowSuffix(){
		var allow="";
		for(var k in g_allow_suffix){
			allow+=k+" ";
		}
		return allow;
	}
	this.ajaxFileUpload=function(obj)
	{
		g_filepath=$(obj).val();
		var filename=getFileName(g_filepath);
		if(!filename){
			return false;
		}
		if(!g_allow_suffix[filename[2].toLowerCase() ]){
			showMsg("请上传:"+getAllowSuffix()+"格式的图片，大小不超过1MB","msg_err");
			return;
		}

		readURL(obj, '#avatar_photo');
        showMsg("上传成功,请选择头像区域","msg_ok");
        $("#div_avatar_edit").fadeIn(500);
		$("#div_avatar_upload").fadeIn(500);

		return false;
	}
	function func_getsuffix(){
		var filename=getFileName(g_filepath);
		if(filename)
			return filename[2];
		return "";
	}

	var g_selection;
	var g_resize;
	function update_preview(){
		if(!g_selection )
			return;
		var selection=g_selection;
		var width=$("#avatar_photo").innerWidth();
		var height=$("#avatar_photo").innerHeight();

		var p_width=$("#avatar_preview").innerWidth();
		var p_height=$("#avatar_preview").innerHeight();
		if( selection.width==0 || selection.height==0)
			return ;

		var scaleX = p_width / selection.width;
		var scaleY = p_height / selection.height;
		g_resize = [Math.round(scaleX * width), Math.round(scaleY * height),
		            Math.round(scaleX * selection.x1), Math.round(scaleY * selection.y1)];
		$('#avatar_preview img').fadeIn(0);
		$('#avatar_preview img').attr("src",$("#avatar_photo").attr("src"));
		$('#avatar_preview img').css({
			width: Math.round(scaleX * width),
			height: Math.round(scaleY * height),
			marginLeft: -Math.round(scaleX * selection.x1),
			marginTop: -Math.round(scaleY * selection.y1)
		});
	}
	this.func_edit_avatar=function (){

        if(!g_selection)
			return;
        var image = $('#avatar_preview img').attr('src');
		var base64ImageContent = image.replace(/^data:image\/(png|jpg|jpeg);base64,/, "");
        var blob = base64ToBlob(base64ImageContent, 'image/png');
        var formData = new FormData();
        formData.append('picture', blob);
        formData.append('size', g_resize);
        $.ajax({
            url: '/user/avatar/upload/',
            type: 'POST',
            data: formData,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            cache: false,
            contentType: false,
            processData: false,
            success: function (data) {
                if (data.status=='Ok'){
//                    $('.account-avatar img').attr("src",data.avatar_url);
                    showMsg("编辑成功，请耐心等待管理员审核","msg_result");
                    $("#photo_select").fadeOut(500);
                    $("#div_avatar_edit").fadeOut(500);
                    $("#div_avatar_upload").fadeOut(500);

                    $.toast({heading:'Success!',text:data.msg, position: 'top-center', icon:'Success'});
                }else{

                    $.toast({heading:'出错拉', text:data.msg, position: 'top-center', icon:'error'});
                }
            },
            error: function (jqXHR, textStatus, errorThrown) {
                $("#sidebar-file-upload").val('');
                $('#sidebar-content').text('')
            }
        });
        return false;
	};
	function func_photo_load()
	{
		var ias=$("#avatar_photo");
		ias.css({width:'auto',height:'auto'});
		g_selection=$.avatarUpload.imgSelector.getSelection();
		update_preview();
	}

	this.avatar_preview=function (img, selection) {
		if (!selection.width || !selection.height)
			return;
		g_selection=selection;
		update_preview();
	}
	function init(){
		$("#div_avatar_edit").fadeOut(0);
		$.avatarUpload.imgSelector=$('#avatar_photo')
		 .imgAreaSelect({instance: true,
		                 aspectRatio: '1:1',
		                 handles: true,
		                 fadeSpeed: 200,
		                 maxHeight:300 ,
		                 parent:"#photo_select",
		                 onSelectChange: $.avatarUpload.avatar_preview,
		                 x1:0,y1:0,x2:1,y2:1});
		$("#avatar_photo").load(func_photo_load);
		showMsg("上传"+getAllowSuffix()+"格式文件","msg_ok");
	}
	this.init=function(container,path){
		if(undefined==path)
			path="upload.html";
		if(undefined==container){
			init();
		}else{
			$.get(path,function(data){
				$(container).html(data);
				init();
			});
		}
	}
}
