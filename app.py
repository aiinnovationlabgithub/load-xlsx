from flask import Flask, request, render_template, jsonify
import pandas as pd
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score
import json
app = Flask(__name__)

@app.route('/result', methods=['GET'])
def result():
    return render_template('result.html')

@app.route('/pre_view', methods=['GET'])
def pre_view():
    return render_template('pre_view.html')

@app.route('/pre_view2', methods=['GET'])
def pre_view2():
    return render_template('pre_view2.html')

@app.route("/submit", methods=['POST'])
def submit():
    
    if 'clientFile' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['clientFile']

    if file:
        #df_true = pd.read_excel('test_final.xlsx')
        df_true = pd.read_excel('ans.xlsx')
        df_true = df_true.drop_duplicates(subset='會員編號', keep='first') # 根據會員編號移除重複值，只保留第一次出現的資料
        print(df_true['會員編號'])
        df_pre = pd.read_excel(file)
        df_pre = df_pre.drop_duplicates(subset='會員編號', keep='first') # 根據會員編號移除重複值，只保留第一次出現的資料
        result_left = pd.merge(df_true, df_pre, on='會員編號', how='left')
        print("Left Join:\n", result_left)
        
        '''
        conf_matrix = confusion_matrix( result_left['label_y'],result_left['label_x'], labels=['loyal', 'partial churn', 'churn'])
        print(conf_matrix)
        print("成功")
        # 計算準確率
        accuracy = accuracy_score(result_left['label_x'], result_left['label_y'])
        '''
        
        labels = ['loyal', 'partial churn', 'churn']

        # 找出實際出現的標籤
        unique_labels = set(result_left['label_y'].dropna().unique())
        valid_labels = set(labels)
        has_valid_data = len(valid_labels & unique_labels) > 0

        if has_valid_data:
            print(has_valid_data)
            conf_matrix = confusion_matrix(result_left['label_y'], result_left['label_x'], labels=labels)
            accuracy = accuracy_score(result_left['label_x'], result_left['label_y'])
        else:
            conf_matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            accuracy = 0.0
        
        print(f"Accuracy: {accuracy:.2f}")
        # 顯示混淆矩陣並標注標籤名稱
        # disp = ConfusionMatrixDisplay(confusion_matrix=conf_matrix, display_labels=['loyal', 'p_churn', 'churn'])
        # disp.plot(cmap=plt.cm.Blues) 
            
        #label = tk.Label(root, text='準確率:'+str(accuracy), font=("Helvetica", 16))
        #label.pack(padx=20, pady=20)
        print('準確率:'+str(accuracy))
        #test = json.dumps(json.loads(result_left.to_json(orient="records")))
        excel_data = json.loads(result_left.to_json(orient="records"))
        #print(result_left['會員編號'])
        matrix = {
            "1":str(conf_matrix[0][0]),
            "2":str(conf_matrix[0][1]),
            "3":str(conf_matrix[0][2]),
            "4":str(conf_matrix[1][0]),
            "5":str(conf_matrix[1][1]),
            "6":str(conf_matrix[1][2]),
            "7":str(conf_matrix[2][0]),
            "8":str(conf_matrix[2][1]),
            "9":str(conf_matrix[2][2]),
        }
        print(matrix)
        
        #pre_view時del label_x資料
        print(request.form.get('kind'))
        if( request.form.get('kind') == "pre_view" or request.form.get('kind') == "pre_view2"):
            for i in range(0, len(excel_data)):
                del excel_data[i]["label_x"]

        data = {"status": "true" ,"data": excel_data, "accuracy":str(accuracy), "matrix": matrix}

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)