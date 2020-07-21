class Apriori:
    def __init__(self, dataset, min_support=0.5, min_conf=0.6):
        # 数据集
        self.dataset = dataset
        # 最小支持度
        self.min_support = min_support
        # 最小置信度
        self.min_conf = min_conf

    def load_data(self):
        """
        测试数据
        :return:
        """
        list = [[1, 3, 4], [2, 3, 5], [1, 2, 3, 5], [2, 5]]
        return list

    def create_c1(self):
        """
        扫描全部数据，产生候选1-项集的集合C1
        :return:
        """
        C1 = []
        for transaction in self.dataset:
            for item in transaction:
                if not [item] in C1:
                    C1.append([item])
        C1.sort()
        # 使用frozenset是为了后面可以将这些值作为字典的键
        return list(map(frozenset, C1))  # frozenset一种不可变的集合

    def generate_lk(self, ck, support_data):
        """
        通过候选项集ck生成频繁项集lk，并将频繁项的支持度保存到support_data字典中
        :param ck: 候选项集ck
        :param support_data: 频繁项集支持度
        :return:
        """
        # 用于标记各候选项在数据集出现的次数
        item_count = {}
        Lk = []
        for t in self.dataset:  # 遍历数据集
            for item in ck:
                # 检查候选集ck中的每一项item是否是t的子集
                if item.issubset(t):
                    if item not in item_count:
                        item_count[item] = 1
                    else:
                        item_count[item] += 1
        # 最小支持度是小数百分比形式
        if self.min_support > 0 and self.min_support < 1:
            t_num = float(len(self.dataset))
        # 最小支持度是整数形式
        else:
            t_num = 1
        # 将满足支持度的候选项添加到频繁项集中
        for item in item_count:
            # 计算item的支持度
            support = item_count[item] / t_num
            if support >= self.min_support:
                Lk.append(item)
                support_data[item] = item_count[item] / t_num
        return Lk

    def create_ck(self, Lk_1, k):
        """
        根据k-1的频繁项集获得k的候选集
        :param Lk_1: 第k-1次的频繁项集
        :param k: 第k次候选集中每个项集的大小，显然第k次就是k，例如[{4}，{5}]就是1， [{1，4}，{3，5}]就是2
        :return: 第k次的候选集ck
        """
        Ck = []
        len_Lk_1 = len(Lk_1)
        lk_list = list(Lk_1)
        # 两次遍历Lk-1，找出前n-1个元素相同的项
        for i in range(len_Lk_1):
            for j in range(i + 1, len_Lk_1):
                l1 = list(lk_list[i])
                l2 = list(lk_list[j])
                l1.sort()
                l2.sort()
                # 前k-2个项一样，即只有最后一项不同时，生成下一候选项
                if l1[0:k - 2] == l2[0:k - 2]:
                    # 求并集
                    Ck_item = lk_list[i] | lk_list[j]
                    # 检查该候选项的子集是否都在Lk-1中
                    if self.check_subset_is_frequent(Ck_item, Lk_1):
                        Ck.append(Ck_item)
        return Ck

    def check_subset_is_frequent(self, ck_item, lk_1):
        """
        检查候选项ck_item的子集是否都在lk-1中
        Apriori算法性质：
        性质1： 频繁项集的所有⾮空⼦集必为频繁项集。
        性质2： ⾮频繁项集的超集⼀定是⾮频繁的。
        :param ck_item: 在第k轮候选项集产生过程中的一个项
        :param lk_1: 第k-1轮获得的频繁项集
        :return:
        """
        for item in ck_item:
            sub_Ck = ck_item - frozenset([item])
            # 该集合的子集不在频繁项集中，说明该集合也不是频繁项集，则不进行添加
            if sub_Ck not in lk_1:
                return False
        return True

    def apriori(self):
        """
        生成频繁项集和支持度
        Apriori算法步骤
        1.扫描全部数据，产生候选1-项集的集合C1.
        2.根据最小支持度，由候选1-项集的集合C1产生频繁1-项集的集合L1.
        3.对k>1,重复执行步骤4,5,6
        4.由Lk执行连接和减枝操作，产生候选k+1-项集的集合Ck+1
        5.根据最小支持度，由候选（k+1）-项集的集合Ck+1，产生频繁（k+1）-项集的集合Lk+1
        6.若L不等于∅，则k=k+1，步骤跳4，否则结束
        7.根据最小置信度，由频繁项集产生强关联规则，结束
        :return: L 频繁项集， support_data 支持度
        """
        # 用于保存各频繁项的支持度
        support_data = {}
        # 扫描全部数据，产生候选1-项集的集合C1
        C1 = self.create_c1()
        # 根据最小支持度，由候选1-项集的集合C1产生频繁1-项集的集合L1，即此时 k=1
        L1 = self.generate_lk(ck=C1, support_data=support_data)
        # 用于保存所有的频繁项集
        L = []
        # 初始化k-1轮的频繁项集为L1
        L_pre = L1.copy()
        L.append(L_pre)
        k = 2
        while(True):
            # 由Lk-1执行连接和减枝操作，产生候选k项集的集合Ck,即此时 k>1
            Ck = self.create_ck(Lk_1=L_pre, k=k)
            # 产生频繁k-项集的集合Lk
            Lk = self.generate_lk(ck=Ck, support_data=support_data)
            # 检查k轮的频繁项集是否存在
            if len(Lk) == 0:
                break
            else:
                # 更新频繁项集为Lk,为k+1轮做好准备
                L_pre = Lk.copy()
                L.append(L_pre)
                k += 1
        # 根据频繁项集和支持度生成关联规则
        rule_list = self.generate_rules(L, support_data)
        return L, support_data, rule_list

    def generate_rules(self, L, support_data):
        """
        根据频繁项集和支持度生成关联规则
        :param L: 频繁项集
        :param support_data: 支持度
        :return: rule_list 关联规则
        """
        rule_list = []  # 保存满足置信度的规则
        sub_set_list = []  # 该数组保存检查过的频繁项
        for i in range(0, len(L)):
            for freq_set in L[i]:  # 遍历Lk
                for sub_set in sub_set_list:  # sub_set_list中保存的是L1到Lk-1
                    if sub_set.issubset(freq_set):  # 检查sub_set是否是freq_set的子集
                        # 检查置信度是否满足要求，是则添加到规则
                        conf = support_data[freq_set] / support_data[sub_set]
                        big_rule = (sub_set, freq_set - sub_set, conf)
                        if conf >= self.min_conf and big_rule not in rule_list:
                            rule_list.append(big_rule)
                sub_set_list.append(freq_set)
        rule_list = sorted(rule_list, key=lambda x: (x[2]), reverse=True)
        return rule_list


if __name__ == '__main__':
    print('')
    # name = get_frequent_cooperation_by_id(cc, 1314124)
    # print(name)
