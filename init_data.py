from database import SessionLocal, User, TimeSlot, Venue, UserPreference
from datetime import datetime, timedelta
import json

def init_fake_data():
    db = SessionLocal()
    
    # 检查是否已有数据
    if db.query(User).count() > 0:
        print("数据已存在，跳过初始化")
        return
    
    # 创建假用户
    users_data = [
        {"name": "张小明", "email": "zhang@example.com", "bio": "AI工程师，喜欢讨论技术和创业"},
        {"name": "李小红", "email": "li@example.com", "bio": "产品经理，对用户体验和商业模式很感兴趣"},
        {"name": "王小华", "email": "wang@example.com", "bio": "设计师，热爱创意和美学，也关注科技趋势"},
        {"name": "刘小强", "email": "liu@example.com", "bio": "销售总监，善于建立人际关系，喜欢户外运动"},
        {"name": "陈小美", "email": "chen@example.com", "bio": "数据科学家，专注机器学习，业余时间喜欢阅读"}
    ]
    
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
    
    db.commit()
    
    # 为每个用户创建时间槽（接下来一周的时间）
    users = db.query(User).all()
    base_date = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    
    for user in users:
        # 每个用户在接下来7天内有一些可用时间
        for day in range(1, 8):  # 明天开始的7天
            date = base_date + timedelta(days=day)
            
            # 上午时间槽 (9:00-12:00)
            if day % 2 == user.id % 2:  # 错开一些用户的时间
                morning_start = date.replace(hour=9)
                morning_end = date.replace(hour=12)
                time_slot = TimeSlot(
                    user_id=user.id,
                    start_time=morning_start,
                    end_time=morning_end,
                    status="available"
                )
                db.add(time_slot)
            
            # 下午时间槽 (14:00-17:00)
            if day % 3 != user.id % 3:  # 不同的用户有不同的可用时间
                afternoon_start = date.replace(hour=14)
                afternoon_end = date.replace(hour=17)
                time_slot = TimeSlot(
                    user_id=user.id,
                    start_time=afternoon_start,
                    end_time=afternoon_end,
                    status="available"
                )
                db.add(time_slot)
            
            # 晚上时间槽 (18:00-21:00)
            if day % 4 == user.id % 2:
                evening_start = date.replace(hour=18)
                evening_end = date.replace(hour=21)
                time_slot = TimeSlot(
                    user_id=user.id,
                    start_time=evening_start,
                    end_time=evening_end,
                    status="available"
                )
                db.add(time_slot)
    
    # 创建假餐厅/咖啡店数据
    venues_data = [
        {"name": "星巴克中关村店", "type": "coffee", "price_range": "$$", "location": "中关村大街1号", "description": "安静的工作环境，适合商务会谈"},
        {"name": "瑞幸咖啡", "type": "coffee", "price_range": "$", "location": "知春路29号", "description": "快捷便利，性价比高"},
        {"name": "蓝山咖啡", "type": "coffee", "price_range": "$$$", "location": "五道口华清嘉园", "description": "精品咖啡，环境优雅"},
        {"name": "海底捞火锅", "type": "restaurant", "price_range": "$$$", "location": "欧美汇购物中心", "description": "服务一流的火锅店，适合深度交流"},
        {"name": "外婆家", "type": "restaurant", "price_range": "$$", "location": "华联商厦", "description": "江浙菜，环境温馨，价格适中"},
        {"name": "西贝莜面村", "type": "restaurant", "price_range": "$$", "location": "中关村欧美汇", "description": "西北菜，分量足，适合聊天"},
        {"name": "胡大饭馆", "type": "restaurant", "price_range": "$", "location": "簋街", "description": "小龙虾专门店，轻松氛围"},
        {"name": "鼎泰丰", "type": "restaurant", "price_range": "$$$", "location": "王府井APM", "description": "台式料理，环境安静优雅"}
    ]
    
    for venue_data in venues_data:
        venue = Venue(**venue_data)
        db.add(venue)
    
    # 添加一些用户偏好（为未来AI分析预留）
    preferences_data = [
        {"user_id": 1, "preference_type": "interest", "preference_value": "人工智能"},
        {"user_id": 1, "preference_type": "game", "preference_value": "英雄联盟"},
        {"user_id": 2, "preference_type": "interest", "preference_value": "产品设计"},
        {"user_id": 2, "preference_type": "team", "preference_value": "湖人队"},
        {"user_id": 3, "preference_type": "interest", "preference_value": "UI设计"},
        {"user_id": 4, "preference_type": "sport", "preference_value": "跑步"},
        {"user_id": 5, "preference_type": "interest", "preference_value": "机器学习"}
    ]
    
    for pref_data in preferences_data:
        preference = UserPreference(**pref_data)
        db.add(preference)
    
    db.commit()
    db.close()
    print("假数据初始化完成！")

if __name__ == "__main__":
    init_fake_data()