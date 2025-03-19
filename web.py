from flask import Flask, request, jsonify, render_template_string
app = Flask(__name__)


def compute_time(distance, speed):
    all_s = float(speed.split("'")[0]) * 60 + float(speed.split("'")[1])
    all_time = distance * all_s
    all_h = int(all_time // 3600)
    all_min = int(all_time % 3600 // 60)
    all_s = int(all_time % 3600 % 60)
    final_time = "{}h{}min{}s".format(all_h, all_min, all_s)
    # print("{}km".format(distance), speed, final_time)
    return "{}km {} {}".format(distance, speed, final_time)

def compute_time_split(distance, speed):
    all_s = float(speed.split("'")[0]) * 60 + float(speed.split("'")[1])
    all_time = distance * all_s
    all_h = int(all_time // 3600)
    all_min = int(all_time % 3600 // 60)
    all_s = int(all_time % 3600 % 60)
    final_time = "{}h{}min{}s".format(all_h, all_min, all_s)
    print("{}km".format(distance), speed, final_time)
    return all_h, all_min, all_s

def compute_distance(speed, time):
    all_s = float(speed.split("'")[0]) * 60 + float(speed.split("'")[1])
    all_t = float(time.split("h")[0]) * 3600 + float(time.split("h")[1].split("min")[0]) * 60 + float(time.split("h")[1].split("min")[1].split("s")[0])
    all_d = round(all_t / all_s, 2)
    # print("{}km".format(all_d), speed, time)
    return "{}km {} {}".format(all_d, speed, time)

def compute_speed(distance, time):
    all_t = float(time.split("h")[0]) * 3600 + float(time.split("h")[1].split("min")[0]) * 60 + float(time.split("h")[1].split("min")[1].split("s")[0])
    all_s = all_t / distance
    s_min = int(all_s // 60)
    s_s = int(all_s % 60)
    final_s = "{}'{:0>2d}".format(s_min, s_s)
    # print("{}km".format(distance), final_s, time)
    return "{}km {} {}".format(distance, final_s, time)

def sub_all_time(d1, s1, d2, s2):
    all_h1, all_min1, all_s1 = compute_time_split(d1, s1)
    all_h2, all_min2, all_s2 = compute_time_split(d2, s2)
    all_h3 = all_h2 + all_h1
    all_min3 = all_min2 + all_min1
    all_s3 = all_s2 + all_s1
    if all_s3 >= 60:
        all_min3 += (all_s3 // 60)
        all_s3 = all_s3 % 60
    elif all_min3 >= 60:
        all_h3 += (all_min3 // 60)
        all_min3 = all_min3 % 60
    final_time = "{}h{}min{}s".format(all_h3, all_min3, all_s3)
    final_s = compute_speed(d1+d2, final_time)
    return final_s

# 定义数学计算函数
def calculate(operation, params):
    if operation == "time":
        return compute_time(float(params[0]), params[1])
    elif operation == "distance":
        return compute_distance(params[0], params[1])
    elif operation == "speed":
        return compute_speed(float(params[0]), params[1])
    elif operation == "up_down":
        return sub_all_time(float(params[0]), params[1], float(params[2]), params[3])
    else:
        raise ValueError("不支持的操作符")


# 主页面：显示输入表单和结果区域
@app.route('/', methods=['GET'])
def index():
    # 渲染 HTML 页面
    return render_template_string('''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>一个计算器小工具</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .container { max-width: 600px; margin: auto; }
                input, select, button { width: 100%; padding: 10px; margin: 5px 0; }
                .hidden { display: none; } /* 隐藏未使用的输入框 */
                .result { margin-top: 20px; font-weight: bold; }
                .error { color: red; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>一个计算器小工具</h1>
                <p>请选择函数并输入参数：</p>
                <form id="string-form">
                    <label for="operation">函数：</label>
                    <select id="operation" name="operation" required>
                        <option value="time">计算耗时</option>
                        <option value="distance">计算距离</option>
                        <option value="speed">计算配速</option>
                        <option value="up_down">根据上下坡配速计算总配速</option>
                    </select><br>

                    <!-- 参数容器 -->
                    <div id="param-container"></div>

                    <button type="submit">执行</button>
                </form>

                <!-- 结果显示区域 -->
                <div id="result" class="result"></div>
            </div>

            <!-- JavaScript 实现动态参数切换和 AJAX 提交 -->
            <script>
                // 定义不同操作符对应的参数配置
                const paramConfig = {
                    time: [
                        { label: "距离km", defaultValue: 20.1 },
                        { label: "配速", defaultValue: "5'12" }
                    ],
                    distance: [
                        { label: "配速", defaultValue: "5'12" },
                        { label: "时间", defaultValue: "2h21min02s" }
                    ],
                    speed: [
                        { label: "距离km", defaultValue: 20.1 },
                        { label: "时间", defaultValue: "1h28min21s" },
                    ],
                    up_down: [
                        { label: "上坡距离km", defaultValue: 10.2 },
                        { label: "上坡配速", defaultValue: "14'01" },
                        { label: "下坡距离km", defaultValue: 8.2 },
                        { label: "下坡配速", defaultValue: "5'30" }

                    ]
                };

                // 更新参数输入框
                function updateParams(operation) {
                    const container = document.getElementById('param-container');
                    container.innerHTML = ''; // 清空容器

                    // 获取当前操作符的参数配置
                    const params = paramConfig[operation];
                    params.forEach((param, index) => {
                        const div = document.createElement('div');
                        div.innerHTML = `
                            <label for="param${index + 1}">${param.label}：</label>
                            <input type="text" id="param${index + 1}" name="param${index + 1}" value="${param.defaultValue}" required><br>
                        `;
                        container.appendChild(div);
                    });
                }

                // 初始化时加载默认参数
                const operationSelect = document.getElementById('operation');
                updateParams(operationSelect.value);

                // 监听操作符变化
                operationSelect.addEventListener('change', function() {
                    updateParams(this.value);
                });

                // 处理表单提交
                document.getElementById('string-form').addEventListener('submit', function(event) {
                    event.preventDefault(); // 阻止表单默认提交行为

                    // 获取表单数据
                    const operation = operationSelect.value;
                    const params = [];
                    const paramConfigForOperation = paramConfig[operation];
                    paramConfigForOperation.forEach((param, index) => {
                        const input = document.getElementById(`param${index + 1}`);
                        params.push(input.value.trim());
                    });

                    // 发送 AJAX 请求
                    fetch('/process', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            params: params.filter(p => p !== ''),
                            operation: operation
                        })
                    })
                    .then(response => response.json())
                    .then(data => {
                        // 显示结果或错误信息
                        const resultDiv = document.getElementById('result');
                        if (data.error) {
                            resultDiv.innerHTML = `<span class="error">${data.error}</span>`;
                        } else {
                            resultDiv.innerHTML = `结果：<pre>${data.result}</pre>`;
                        }
                    })
                    .catch(error => {
                        console.error('请求失败:', error);
                        document.getElementById('result').innerHTML = '<span class="error">服务器内部错误</span>';
                    });
                });
            </script>
        </body>
        </html>
    ''')


# 处理 AJAX 请求并返回 JSON 结果
@app.route('/process', methods=['POST'])
def string_process():
    try:
        # 获取 JSON 数据
        data = request.get_json()
        operation = data.get('operation')  # 操作符
        params = data.get('params')  # 字符串列表

        # 执行处理
        result = calculate(operation, params)

        # 返回 JSON 格式的结果
        return jsonify({"result": result})

    except ValueError as e:
        # 捕获错误并返回错误信息
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        # 捕获其他异常
        return jsonify({"error": "服务器内部错误"}), 500



# 启动应用
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8100)
    # app.run(debug=True)


