$(function(){
	setTimeout(function(){
		var souid_arr = $("#test-main").attr('souid').split(',');
		if(souid_arr.length<2){
			layer.alert('请选择相应组件进行连接', {
				icon: 2,
				title: '提示'
			});
		};
				var actId = '';
		var inputID = '';
		for(var i=0;i<souid_arr.length;i++){
			if(souid_arr[i].substring(0,7)==='AtomAct'){
				actId = souid_arr[i]
			}else{
				inputID = souid_arr[i]
			}
		};
		//load数据
		$.ajax({
			type:'post',
			url:server+'/atom_test/load',
			data:{
				project_id:proid,
				component_id:$("#test-main").attr('data'),
				atom_act_id:actId,
				input_comp_id:inputID
			},
			success:function(data){
				function success(){
					var datas = dataBack(data).detail;
					if(datas!=null){
						$("#c_id_variable").text(datas.id);
						$("#target_variable").text(datas.target);
						$("#classification_score").val(datas.max_value)
						$("#target_variable").addClass('load_test');
						$("#c_id_variable").addClass('load_test');
					}
					
				}
				backInfo(data,success)
			},
			error: function(data) {
				layer.msg('接口请求失败');
			}
		});
				var line_type = '';
		for(i in souid_arr){
			if(souid_arr[i].substring(0,7)!='AtomAct'){
				line_type = souid_arr[i]
			}
		}
		//获取hivereader数据
		$.ajax({
			type: 'post',
			url: server + '/csv_reader/loadFieldType??' + timeStamp,
			data: {
				project_id: proid,
				component_id:line_type,
			},
			success: function(data) {
				function success() {
					var fields = dataBack(data).detail;
					var str = ''
					for(i in fields){
						if(fields[i].selected==true){
						str+= '<li title="'+fields[i].field+'">'+fields[i].field+'</li>'
							
						}

					}
					$("#test_id").append(str);
					$("#test_target").append(str);
				}
				backInfo(data, success)
			},
			error: function(data) {
				layer.msg('接口请求失败');
			}
		})
	},10)
		//下拉列表展开
	$(".c_nav_list-test").click(function(){
		if($(this).next().is(':hidden')){
			$(this).next().show();
		}
	});
	$(".onther_ul").on('click','li',function(){
		$(this).parent().prev().find('em').text($(this).text());
		$(this).parent().prev().find('em').css('color','#858585')
		$(this).parent().hide();
        $(this).parent().parent().find(".error_test").hide();

	})
	$(".c-test-save").click(function(){
        if(($("#c_id_variable").text() === '点击选择变量')||($("#target_variable").text() === '点击选择变量')){
            if($("#c_id_variable").text() === '点击选择变量') {
                $("#c_id_variable").parent().siblings('.error_test').show()
            }
            if($("#target_variable").text() === '点击选择变量') {
                $("#target_variable").parent().siblings('.error_test').show()
            }
		}else{
            $("#c_id_variable").parent().siblings('.error_test').hide()
            $("#target_variable").parent().siblings('.error_test').hide()
            var souidArr = $("#test-main").attr('souid').split(',');
            if( $("#test-main").attr('souid')===''){
                alert('请链接相应组件')
            }else if(souidArr.length===1&&souidArr[0].substring(0,7)==='AtomAct'){
                alert('请连接一份数据')
            }else{

                var actId = '';
                var inputID = '';
                for(var i=0;i<souidArr.length;i++){
                    if(souidArr[i].substring(0,7)==='AtomAct'){
                        actId = souidArr[i]
                    }else{
                        inputID = souidArr[i]
                    }
                };
                $.ajax({
                    type:'post',
                    url:server+'/atom_test/saveInfo?'+timeStamp,
                    data:{
                        project_id:proid,
                        component_id:$("#test-main").attr('data'),
                        atom_act_id:actId,
                        input_comp_id:inputID,
                        feature_id:$("#c_id_variable").text(),
                        feature_target:$("#target_variable").text(),
//					max_value:$("#classification_score").val()
                    },
                    success:function(data){
                        function success(){
                            alertSuccess()
                        };
                        backInfo(data,success)
                    },
                    error: function(data) {
                        layer.msg('接口请求失败');
                    }
                })
            }

        }


	});
	$(".run").click(function(){
		runParameter($("#test-main").attr('data'))
		$("#runContent").fadeIn()
		$("#shadowBody").show()
	});
	    $('#classification_score').blur(function(){
        var str = $('#classification_score').val();
        var reg = /^(\+?[1-9]\d{0,2}|\+?1000)$/;
        if( str != '' ){
            if( reg.test(str) ){
               $('.c-test-score>p').hide();
            }else{
               $('.c-test-score>p').show();
           };
        };
    });
})
