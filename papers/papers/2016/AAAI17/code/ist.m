num_classifiers = 25; %�趨�ж��ٸ�������
num_round = 100; %�趨ѭ������

prob_base = 100; %�ٶ�������Ϊ6

        prob = prob_base / 200 + randn(1, num_classifiers) / 6; %���ɸ�

        c = zeros(num_classifiers, 1); %min c'x
        A = ones(1, num_classifiers); %Ax = b
        b = 1; %Ax = b
        B = 1; %Basic feasible solution
        o = 0; %���Ž��ֵ
        a = [1; zeros(num_classifiers - 1, 1)]; %a�Ľ�
        
        
        co = zeros(num_classifiers, 1); %min c'x
        Ao = ones(1, num_classifiers); %Ax = b
        bo = 1; %Ax = b
        Bo = 1; %Basic feasible solution
        oo = 0; %���Ž��ֵ
        ao = [1; zeros(num_classifiers - 1, 1)]; %a�Ľ�

        iter_list = [];
        iterreal_list = [];

        for num_training_data = 1 : num_round %ѵ�����ݸ���
            
            new = sign(rand(1, num_classifiers) - 1/2 + prob); %�����ɵ�Ԥ������

            %����ѵ������
            c = [c; -1; 0]; 
            A = [A, zeros(num_training_data, 2); -new, zeros(1, 2 * (num_training_data-1)), -1, 1];
            B = [B; num_classifiers + 2 * num_training_data];
            b = [b; 0];

            co = [co; -1; 0]; 
            Ao = [Ao, zeros(num_training_data, 2); -new, zeros(1, 2 * (num_training_data-1)), -1, 1];
            Bo = [Bo; num_classifiers + 2 * num_training_data];
            bo = [bo; 0];

            %��������
            comb = [-A(num_training_data + 1, B(1 : num_training_data)), 1];
            
            A(num_training_data + 1, :) = comb * A;
            b(num_training_data + 1) = comb * b;
            
            comb = [-Ao(num_training_data + 1, Bo(1 : num_training_data)), 1];
            Ao(num_training_data + 1, :) = comb * Ao;
            bo(num_training_data + 1) = comb * bo;
            
            o_list = []; %��¼��ͬ���������µĽ��
            oo_list = []; 
            for iter = 1 : 100 %����ʮ��            
                pivot_row = 0;  %����
                pivot_column = 0; %����
                max_increase = -1000; 
                %ѡ����ʵ��к���
                for i = 1 : num_training_data + 1
                    if b(i) < -0.00001
                        min_factor = 1000;
                        min_factor_column = 0;
                        for j = 1 : 2 * num_training_data + num_classifiers
                            if A(i, j) < -0.00001
                                if min_factor > c(j) / A(i, j) - 0.00001
                                    min_factor = c(j) / A(i, j);
                                    min_factor_column = j;
                                end
                            end
                        end
                        if min_factor_column > 0
                            if max_increase < -min_factor * b(i) - 0.00001
                                max_increase = -min_factor * b(i);
                                pivot_column = min_factor_column;
                                pivot_row = i;
                            elseif max_increase < -min_factor * b(i) + 0.00001
                                if B(i) > B(pivot_row)
                                    pivot_column = min_factor_column;
                                    pivot_row = i;
                                end
                            end
                        end
                    end
                end

                %����
                if pivot_row > 0
                    if B(pivot_row) <= num_classifiers
                        a(B(pivot_row)) = 0;
                    end
                    B(pivot_row) = pivot_column;
                    factor = A(pivot_row, pivot_column);
                    A(pivot_row, :) = A(pivot_row, :) / factor;
                    b(pivot_row) = b(pivot_row) / factor;
                    if B(pivot_row) <= num_classifiers
                        a(B(pivot_row)) = b(pivot_row);
                    end
                    for i = 1 : num_training_data + 1
                        if i ~= pivot_row
                            factor = -A(i, pivot_column);
                            A(i, :) = A(i, :) + factor * A(pivot_row, :);
                            b(i) = b(i) + factor * b(pivot_row);
                            if B(i) <= num_classifiers
                                a(B(i)) = b(i);
                            end
                        end
                    end
                   
                    factor = -c(pivot_column);
                    factor
                    c = c + factor * A(pivot_row, :)';                  
                    o = o + factor * b(pivot_row);
                    o
                    o_list = [o_list;o];
                else
                    break
                end
                a
            end
            o_list
            iter_list = [iter_list ; iter];
            
            for iter_real = 1:30
                iter_real
                pivot_row = 0;
                pivot_column = 0;
                max_increase = -1000; 
                %ѡ����ʵ��к���
                for i = 1 : num_training_data + 1
                    if bo(i) < -0.00001
                        min_factor = 1000;
                        min_factor_column = 0;
                        for j = 1 : 2 * num_training_data + num_classifiers
                            if Ao(i, j) < -0.00001
                                if min_factor > co(j) / Ao(i, j) - 0.00001
                                    min_factor = co(j) / Ao(i, j);
                                    min_factor_column = j;
                                end
                            end
                        end
                        if min_factor_column > 0
                            if max_increase < -min_factor * bo(i) - 0.00001
                                max_increase = -min_factor * bo(i);
                                pivot_column = min_factor_column;
                                pivot_row = i;
                            elseif max_increase < -min_factor * bo(i) + 0.00001
                                if Bo(i) > Bo(pivot_row)
                                    pivot_column = min_factor_column;
                                    pivot_row = i;
                                end
                            end
                        end
                    end
                end

                %����
                if pivot_row > 0
                    if Bo(pivot_row) <= num_classifiers
                        ao(Bo(pivot_row)) = 0;
                    end
                    Bo(pivot_row) = pivot_column;
                    factor = Ao(pivot_row, pivot_column);
                    Ao(pivot_row, :) = Ao(pivot_row, :) / factor;
                    bo(pivot_row) = bo(pivot_row) / factor;
                    if Bo(pivot_row) <= num_classifiers
                        ao(Bo(pivot_row)) = bo(pivot_row);
                    end
                    for i = 1 : num_training_data + 1
                        if i ~= pivot_row
                            factor = -Ao(i, pivot_column);
                            Ao(i, :) = Ao(i, :) + factor * Ao(pivot_row, :);
                            bo(i) = bo(i) + factor * bo(pivot_row);
                            if Bo(i) <= num_classifiers
                                ao(Bo(i)) = bo(i);
                            end
                        end
                    end
                    factor = -co(pivot_column);
                    co = co + factor * Ao(pivot_row, :)'; 
                    oo = oo + factor * bo(pivot_row);
                    oo_list=[oo_list;oo];
                else
                    break
                end
            end
            iterreal_list = [iterreal_list;iter_real];
            oo_list
        end
        %iter_list
        %iterreal_list
        
   
   
    
   

