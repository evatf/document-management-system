import re
import os
import sys
from collections import Counter
from difflib import SequenceMatcher, unified_diff, Differ
from io import BytesIO

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTextEdit, QTableWidget,
                             QTableWidgetItem, QHeaderView, QAbstractItemView,
                             QGroupBox, QGridLayout, QSplitter, QFileDialog,
                             QMessageBox, QProgressDialog, QDialog, QTabWidget,
                             QListWidget, QListWidgetItem, QFrame, QScrollArea,
                             QProgressBar, QCheckBox, QSpinBox, QTreeWidget,
                             QTreeWidgetItem, QMenu, QAction, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QImage, QColor, QTextCursor, QFont, QTextCharFormat, QBrush

from core.database import db
from core.document_parser import DocumentParser
from core.styles import (TOOLBAR_PRIMARY_BTN, TOOLBAR_DEFAULT_BTN, TOOLBAR_DANGER_BTN,
                          SEARCH_BOX_STYLE, FILTER_COMBO_STYLE, DIALOG_BTN_PRIMARY,
                          DIALOG_BTN_DEFAULT, STAT_CARD_ENHANCED_STYLE, STAT_NUMBER_STYLE,
                          STAT_LABEL_STYLE, SIMILARITY_NUMBER_STYLE, SECTION_TITLE_STYLE,
                          HINT_LABEL_STYLE, INFO_BAR_STYLE, LIST_ITEM_ENHANCED_STYLE)


STOPWORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
    '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去',
    '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '他',
    '她', '它', '我们', '你们', '他们', '什么', '怎么', '为什么',
    '因为', '所以', '但是', '然而', '如果', '那么', '虽然', '可是',
    '或者', '还是', '以及', '并且', '而且', '此外', '另外', '同时',
    '关于', '对于', '至于', '按照', '根据', '通过', '为了', '由于',
    '除了', '包括', '以及', '等等', '之类', '以上', '以下', '之前',
    '之后', '以来', '以内', '以外', '之间', '之中', '之内', '之外',
    '这个', '那个', '这些', '那些', '每个', '各个', '任何', '所有',
    '已经', '正在', '将要', '曾经', '一直', '总是', '经常', '常常',
    '可以', '能够', '应该', '必须', '需要', '想要', '希望', '愿意',
    '非常', '特别', '十分', '极其', '比较', '相当', '更加', '越来越',
    '起来', '下去', '过来', '过去', '出来', '进去', '上来', '下来',
    '一下', '一下下', '一点', '一点点', '一些', '有些', '有的',
    '第一', '第二', '第三', '第四', '第五', '首先', '其次', '再次',
    '最后', '总之', '综上所述', '由此可见', '因此', '因而', '故而',
    '啊', '吧', '呢', '吗', '哦', '嗯', '呀', '啦', '嘛', '哟', '呗'
])


class AnalysisWorker(QThread):
    """分析工作线程"""
    progress = pyqtSignal(int, int)
    finished_signal = pyqtSignal(dict)
    
    def __init__(self, analysis_type, **kwargs):
        super().__init__()
        self.analysis_type = analysis_type
        self.kwargs = kwargs
    
    def run(self):
        if self.analysis_type == 'wordfreq':
            result = self.analyze_word_frequency()
        elif self.analysis_type == 'compare':
            result = self.compare_documents()
        elif self.analysis_type == 'pattern':
            result = self.extract_patterns()
        elif self.analysis_type == 'similarity':
            result = self.calculate_similarity()
        elif self.analysis_type == 'style':
            result = self.analyze_style()
        elif self.analysis_type == 'structure':
            result = self.analyze_structure()
        else:
            result = {'error': '未知分析类型'}
        
        self.finished_signal.emit(result)
    
    def analyze_word_frequency(self):
        """词频分析"""
        try:
            import jieba
            import jieba.analyse
            
            doc_id = self.kwargs.get('doc_id')
            doc = db.get_document(doc_id)
            
            if not doc or not doc['content_text']:
                return {'error': '文档内容为空'}
            
            text = doc['content_text']
            
            words = jieba.lcut(text)
            
            words = [w for w in words if len(w) > 1 and w not in STOPWORDS]
            
            word_freq = Counter(words).most_common(100)
            
            keywords = jieba.analyse.extract_tags(text, topK=30, withWeight=True)
            
            return {
                'success': True,
                'word_freq': word_freq,
                'keywords': keywords,
                'total_words': len(words),
                'unique_words': len(set(words)),
                'doc_title': doc['title']
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def compare_documents(self):
        """文档比对"""
        try:
            doc1_id = self.kwargs.get('doc1_id')
            doc2_id = self.kwargs.get('doc2_id')
            
            doc1 = db.get_document(doc1_id)
            doc2 = db.get_document(doc2_id)
            
            if not doc1 or not doc2:
                return {'error': '文档不存在'}
            
            text1 = doc1['content_text'] or ''
            text2 = doc2['content_text'] or ''
            
            similarity = SequenceMatcher(None, text1, text2).ratio()
            
            lines1 = text1.splitlines()
            lines2 = text2.splitlines()
            
            differ = Differ()
            diff_lines = list(differ.compare(lines1, lines2))
            
            return {
                'success': True,
                'similarity': similarity,
                'diff_lines': diff_lines,
                'lines1': lines1,
                'lines2': lines2,
                'doc1_title': doc1['title'],
                'doc2_title': doc2['title']
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def extract_patterns(self):
        """提取常用句式"""
        try:
            import jieba
            
            doc_id = self.kwargs.get('doc_id')
            doc = db.get_document(doc_id)
            
            if not doc or not doc['content_text']:
                return {'error': '文档内容为空'}
            
            text = doc['content_text']
            
            sentences = re.split(r'[。！？\n]', text)
            sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
            
            parallel_sentences = []
            for i in range(len(sentences) - 2):
                s1, s2, s3 = sentences[i], sentences[i+1], sentences[i+2]
                if abs(len(s1) - len(s2)) < 10 and abs(len(s2) - len(s3)) < 10:
                    common_start = os.path.commonprefix([s1, s2, s3])
                    if len(common_start) >= 2:
                        parallel_sentences.append((s1, s2, s3))
            
            patterns = [
                (r'坚持(.{2,15})原则', '坚持...原则'),
                (r'以(.{2,15})为(.{2,15})', '以...为...'),
                (r'加强(.{2,15})建设', '加强...建设'),
                (r'推进(.{2,15})发展', '推进...发展'),
                (r'深化(.{2,15})改革', '深化...改革'),
                (r'落实(.{2,15})措施', '落实...措施'),
                (r'完善(.{2,15})机制', '完善...机制'),
                (r'建立健全(.{2,15})', '建立健全...'),
                (r'进一步(.{2,15})', '进一步...'),
                (r'不断(.{2,15})', '不断...'),
                (r'切实(.{2,15})', '切实...'),
                (r'认真(.{2,15})', '认真...'),
                (r'全面(.{2,15})', '全面...'),
                (r'深入(.{2,15})', '深入...'),
                (r'扎实(.{2,15})', '扎实...'),
            ]
            
            fixed_patterns = []
            for pattern, name in patterns:
                matches = re.findall(pattern, text)
                if matches:
                    examples = []
                    for m in matches[:10]:
                        if isinstance(m, tuple):
                            examples.append(name.replace('...', ''.join(m)))
                        else:
                            examples.append(name.replace('...', m))
                    fixed_patterns.append({
                        'name': name,
                        'count': len(matches),
                        'examples': examples
                    })
            
            opening_patterns = []
            closing_patterns = []
            for sent in sentences[:30]:
                if len(sent) > 5:
                    if any(keyword in sent[:10] for keyword in ['为深入', '为认真', '为全面', '为贯彻', '为落实', '根据', '按照', '近日', '近期']):
                        opening_patterns.append(sent)
                    if any(keyword in sent[-10:] for keyword in ['特此通知', '请遵照执行', '请认真贯彻', '以上报告', '特此报告']):
                        closing_patterns.append(sent)
            
            return {
                'success': True,
                'sentences': sentences[:50],
                'parallel_sentences': parallel_sentences[:10],
                'fixed_patterns': fixed_patterns,
                'opening_patterns': opening_patterns[:10],
                'closing_patterns': closing_patterns[:10],
                'doc_title': doc['title'],
                'doc_id': doc_id
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_similarity(self):
        """计算相似度"""
        try:
            import jieba
            from collections import defaultdict
            import math
            
            doc1_id = self.kwargs.get('doc1_id')
            doc2_id = self.kwargs.get('doc2_id')
            
            doc1 = db.get_document(doc1_id)
            doc2 = db.get_document(doc2_id)
            
            if not doc1 or not doc2:
                return {'error': '文档不存在'}
            
            text1 = doc1['content_text'] or ''
            text2 = doc2['content_text'] or ''
            
            words1 = jieba.lcut(text1)
            words2 = jieba.lcut(text2)
            
            def get_word_freq(words):
                freq = defaultdict(int)
                for w in words:
                    if len(w) > 1:
                        freq[w] += 1
                return freq
            
            freq1 = get_word_freq(words1)
            freq2 = get_word_freq(words2)
            
            all_words = set(freq1.keys()) | set(freq2.keys())
            
            dot_product = sum(freq1[w] * freq2[w] for w in all_words)
            magnitude1 = math.sqrt(sum(freq1[w] ** 2 for w in all_words))
            magnitude2 = math.sqrt(sum(freq2[w] ** 2 for w in all_words))
            
            if magnitude1 == 0 or magnitude2 == 0:
                similarity = 0
            else:
                similarity = dot_product / (magnitude1 * magnitude2)
            
            paragraphs1 = [p.strip() for p in text1.split('\n\n') if len(p.strip()) > 20]
            paragraphs2 = [p.strip() for p in text2.split('\n\n') if len(p.strip()) > 20]
            
            similar_paragraphs = []
            for p1 in paragraphs1[:20]:
                for p2 in paragraphs2[:20]:
                    sim = SequenceMatcher(None, p1, p2).ratio()
                    if sim > 0.6:
                        similar_paragraphs.append({
                            'similarity': sim,
                            'p1': p1[:200] + '...' if len(p1) > 200 else p1,
                            'p2': p2[:200] + '...' if len(p2) > 200 else p2
                        })
            
            similar_paragraphs.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                'success': True,
                'similarity': similarity,
                'doc1_title': doc1['title'],
                'doc2_title': doc2['title'],
                'common_words': list(set(freq1.keys()) & set(freq2.keys()))[:30],
                'similar_paragraphs': similar_paragraphs[:10]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_style(self):
        """领导风格学习"""
        try:
            import jieba
            from collections import defaultdict
            
            original_id = self.kwargs.get('original_id')
            revised_id = self.kwargs.get('revised_id')
            
            original = db.get_document(original_id)
            revised = db.get_document(revised_id)
            
            if not original or not revised:
                return {'error': '文档不存在'}
            
            text_original = original['content_text'] or ''
            text_revised = revised['content_text'] or ''
            
            words_original = [w for w in jieba.lcut(text_original) if len(w) > 1 and w not in STOPWORDS]
            words_revised = [w for w in jieba.lcut(text_revised) if len(w) > 1 and w not in STOPWORDS]
            
            freq_original = Counter(words_original)
            freq_revised = Counter(words_revised)
            
            added_words = []
            removed_words = []
            
            for word in freq_revised:
                if word not in freq_original:
                    added_words.append((word, freq_revised[word]))
            
            for word in freq_original:
                if word not in freq_revised:
                    removed_words.append((word, freq_original[word]))
            
            added_words.sort(key=lambda x: x[1], reverse=True)
            removed_words.sort(key=lambda x: x[1], reverse=True)
            
            emphasized_words = []
            for word in freq_revised:
                if word in freq_original:
                    ratio = freq_revised[word] / freq_original[word]
                    if ratio > 1.5 and freq_revised[word] >= 2:
                        emphasized_words.append((word, freq_original[word], freq_revised[word], ratio))
            
            emphasized_words.sort(key=lambda x: x[3], reverse=True)
            
            patterns = [
                r'坚持(.{2,15})原则',
                r'以(.{2,15})为(.{2,15})',
                r'加强(.{2,15})建设',
                r'推进(.{2,15})发展',
                r'深化(.{2,15})改革',
                r'进一步(.{2,15})',
                r'不断(.{2,15})',
                r'切实(.{2,15})',
                r'认真(.{2,15})',
                r'全面(.{2,15})',
                r'深入(.{2,15})',
            ]
            
            def count_patterns(text):
                counts = {}
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        counts[pattern] = len(matches)
                return counts
            
            patterns_original = count_patterns(text_original)
            patterns_revised = count_patterns(text_revised)
            
            style_recommendations = []
            if added_words:
                style_recommendations.append(f"新增高频词汇：{', '.join([w for w, c in added_words[:10]])}")
            if emphasized_words:
                style_recommendations.append(f"强调词汇：{', '.join([w for w, o, r, rt in emphasized_words[:10]])}")
            if patterns_revised:
                style_recommendations.append(f"偏好句式：{len(patterns_revised)}种常用句式")
            
            return {
                'success': True,
                'original_title': original['title'],
                'revised_title': revised['title'],
                'added_words': added_words[:30],
                'removed_words': removed_words[:30],
                'emphasized_words': emphasized_words[:20],
                'patterns_original': patterns_original,
                'patterns_revised': patterns_revised,
                'style_recommendations': style_recommendations
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_structure(self):
        """结构分析"""
        try:
            doc_id = self.kwargs.get('doc_id')
            doc = db.get_document(doc_id)
            
            if not doc or not doc['content_text']:
                return {'error': '文档内容为空'}
            
            text = doc['content_text']
            lines = text.splitlines()
            
            headings = []
            outline_items = []
            
            heading_patterns = [
                (r'^[一二三四五六七八九十]+、', 1),
                (r'^（[一二三四五六七八九十]+）', 1),
                (r'^\([一二三四五六七八九十]+\)', 1),
                (r'^[0-9]+\.', 2),
                (r'^[0-9]+\、', 2),
                (r'^（[0-9]+）', 2),
                (r'^\([0-9]+\)', 2),
                (r'^[0-9]+\.[0-9]+', 3),
                (r'^[0-9]+\.[0-9]+\.[0-9]+', 4),
            ]
            
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                
                level = 0
                for pattern, lvl in heading_patterns:
                    if re.match(pattern, line):
                        level = lvl
                        break
                
                if level == 0 and len(line) < 30 and any(keyword in line for keyword in ['一、', '二、', '三、', '第一章', '第二章', '总则', '附则', '前言', '结语']):
                    level = 1
                
                if level > 0 or (len(line) < 50 and line.endswith(('：', ':', '。', '！', '？'))):
                    if level == 0:
                        level = 2 if len(line) < 20 else 3
                    headings.append({
                        'level': level,
                        'text': line,
                        'line_num': i
                    })
                    outline_items.append({
                        'level': level,
                        'text': line,
                        'line_num': i
                    })
            
            paragraphs = []
            current_paragraph = []
            
            for line in lines:
                if line.strip():
                    current_paragraph.append(line)
                elif current_paragraph:
                    para_text = '\n'.join(current_paragraph)
                    if len(para_text.strip()) > 20:
                        paragraphs.append({
                            'text': para_text[:200] + '...' if len(para_text) > 200 else para_text,
                            'length': len(para_text),
                            'full_text': para_text
                        })
                    current_paragraph = []
            
            if current_paragraph:
                para_text = '\n'.join(current_paragraph)
                if len(para_text.strip()) > 20:
                    paragraphs.append({
                        'text': para_text[:200] + '...' if len(para_text) > 200 else para_text,
                        'length': len(para_text),
                        'full_text': para_text
                    })
            
            key_sentences = []
            for para in paragraphs:
                sentences = re.split(r'[。！？]', para['full_text'])
                for sent in sentences:
                    sent = sent.strip()
                    if len(sent) > 15:
                        if any(keyword in sent for keyword in ['必须', '要', '应该', '坚持', '加强', '推进', '深化', '完善', '建立', '要求', '强调', '指出', '认为', '总之', '综上所述']):
                            key_sentences.append(sent)
                        elif sent.startswith(('一是', '二是', '三是', '第一', '第二', '第三', '首先', '其次', '再次')):
                            key_sentences.append(sent)
            
            key_sentences = list(dict.fromkeys(key_sentences))[:50]
            
            return {
                'success': True,
                'doc_title': doc['title'],
                'outline': outline_items,
                'paragraphs': paragraphs[:30],
                'key_sentences': key_sentences,
                'total_lines': len(lines),
                'total_paragraphs': len(paragraphs),
                'total_headings': len(headings)
            }
            
        except Exception as e:
            return {'error': str(e)}


class ToolCard(QFrame):
    """工具卡片"""
    clicked = pyqtSignal()
    
    def __init__(self, icon, name, desc, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            ToolCard {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 8px;
                padding: 20px;
            }
            ToolCard:hover {
                border-color: #1890ff;
                background-color: #f0f7ff;
            }
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumHeight(140)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        header = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 32px;")
        header.addWidget(icon_label)
        
        name_label = QLabel(name)
        name_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        header.addWidget(name_label)
        header.addStretch()
        
        layout.addLayout(header)
        
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("font-size: 13px; color: #666;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        layout.addStretch()
    
    def mousePressEvent(self, event):
        self.clicked.emit()


class WordCloudWidget(QWidget):
    """词云显示组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel("生成词云中...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: #f5f7fa; border-radius: 8px;")
        self.label.setMinimumHeight(300)
        layout.addWidget(self.label)
    
    def generate_wordcloud(self, word_freq):
        """生成词云"""
        try:
            from wordcloud import WordCloud
            import numpy as np
            from PIL import Image, ImageDraw, ImageFont
            
            if not word_freq:
                self.label.setText("没有足够的词汇生成词云")
                return
            
            freq_dict = {word: freq for word, freq in word_freq if freq > 0}
            
            if not freq_dict:
                self.label.setText("没有足够的词汇生成词云")
                return
            
            width, height = 800, 400
            wc = WordCloud(
                font_path=self._get_font_path(),
                width=width,
                height=height,
                background_color='white',
                max_words=100,
                colormap='viridis',
                prefer_horizontal=0.7
            )
            
            wc.generate_from_frequencies(freq_dict)
            
            img = wc.to_image()
            
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            qimage = QImage.fromData(buf.getvalue())
            pixmap = QPixmap.fromImage(qimage)
            
            self.label.setPixmap(pixmap.scaled(
                self.label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            
        except ImportError:
            self._generate_simple_wordcloud(word_freq)
        except Exception as e:
            self.label.setText(f"词云生成失败: {str(e)}")
    
    def _get_font_path(self):
        """获取字体路径 - 兼容Windows和Linux"""
        from pathlib import Path
        
        font_paths = []
        
        if sys.platform == 'win32':
            font_paths = [
                Path('C:/Windows/Fonts/msyh.ttc'),
                Path('C:/Windows/Fonts/simhei.ttf'),
                Path('C:/Windows/Fonts/simsun.ttc'),
            ]
        else:
            font_paths = [
                Path('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc'),
                Path('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'),
                Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
                Path('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'),
                Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
            ]
        
        for path in font_paths:
            if path.exists():
                return str(path)
        
        return None
    
    def _generate_simple_wordcloud(self, word_freq):
        """简单词云替代方案"""
        text = "高频词汇:\n"
        for i, (word, freq) in enumerate(word_freq[:20]):
            text += f"{i+1}. {word}: {freq}次\n"
        
        self.label.setText(text)


class CompactDiffViewerWidget(QWidget):
    """紧凑版差异比对视图 - 字词级精确比对"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        stats_widget = QWidget()
        stats_widget.setStyleSheet("background-color: white; border: 1px solid #e8e8e8; border-radius: 8px; padding: 15px;")
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(10, 10, 10, 10)
        stats_layout.setSpacing(15)
        
        def create_stat_card(value_text, color, label_text):
            card = QWidget()
            card.setStyleSheet(f"""
                QWidget {{
                    background-color: #fafafa;
                    border-radius: 6px;
                    padding: 8px 15px;
                }}
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            card_layout.setSpacing(2)
            
            value = QLabel(value_text)
            value.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {color};")
            value.setAlignment(Qt.AlignCenter)
            
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 11px; color: #999;")
            label.setAlignment(Qt.AlignCenter)
            
            card_layout.addWidget(value)
            card_layout.addWidget(label)
            return card
        
        self.added_card = create_stat_card("0", "#52c41a", "新增字数")
        stats_layout.addWidget(self.added_card)
        
        self.deleted_card = create_stat_card("0", "#ff4d4f", "删除字数")
        stats_layout.addWidget(self.deleted_card)
        
        self.similarity_card = create_stat_card("0%", "#1890ff", "相似度")
        stats_layout.addWidget(self.similarity_card)
        
        self.original_card = create_stat_card("0", "#333", "原文字数")
        stats_layout.addWidget(self.original_card)
        
        self.modified_card = create_stat_card("0", "#333", "修改稿字数")
        stats_layout.addWidget(self.modified_card)
        
        stats_layout.addStretch()
        layout.addWidget(stats_widget)
        
        legend_widget = QWidget()
        legend_layout = QHBoxLayout(legend_widget)
        legend_layout.setContentsMargins(0, 5, 0, 5)
        legend_layout.setSpacing(20)
        
        legend1 = QLabel("🔴 红色删除线 = 删除的字词")
        legend1.setStyleSheet("font-size: 13px; color: #666;")
        legend_layout.addWidget(legend1)
        
        legend2 = QLabel("🟡 黄色背景 = 新增的字词")
        legend2.setStyleSheet("font-size: 13px; color: #666;")
        legend_layout.addWidget(legend2)
        
        legend_layout.addStretch()
        layout.addWidget(legend_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        
        doc1_container = QWidget()
        doc1_layout = QVBoxLayout(doc1_container)
        doc1_layout.setContentsMargins(0, 0, 0, 0)
        doc1_layout.setSpacing(8)
        
        doc1_header = QLabel("原始稿")
        doc1_header.setStyleSheet("font-size: 15px; font-weight: bold; color: #333; padding: 10px; background: #f5f5f5; border-radius: 4px;")
        doc1_layout.addWidget(doc1_header)
        
        self.text1 = QTextEdit()
        self.text1.setReadOnly(True)
        self.text1.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.8;
            }
        """)
        doc1_layout.addWidget(self.text1, 1)
        
        splitter.addWidget(doc1_container)
        
        doc2_container = QWidget()
        doc2_layout = QVBoxLayout(doc2_container)
        doc2_layout.setContentsMargins(0, 0, 0, 0)
        doc2_layout.setSpacing(8)
        
        doc2_header = QLabel("修改稿")
        doc2_header.setStyleSheet("font-size: 15px; font-weight: bold; color: #333; padding: 10px; background: #f5f5f5; border-radius: 4px;")
        doc2_layout.addWidget(doc2_header)
        
        self.text2 = QTextEdit()
        self.text2.setReadOnly(True)
        self.text2.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                padding: 15px;
                font-size: 14px;
                line-height: 1.8;
            }
        """)
        doc2_layout.addWidget(self.text2, 1)
        
        splitter.addWidget(doc2_container)
        splitter.setSizes([500, 500])
        
        # 同步滚动
        self._syncing = False
        self.text1.verticalScrollBar().valueChanged.connect(lambda v: self._sync_scroll(self.text2, v))
        self.text2.verticalScrollBar().valueChanged.connect(lambda v: self._sync_scroll(self.text1, v))
        
        layout.addWidget(splitter, 1)
    
    def _sync_scroll(self, target, value):
        """同步滚动"""
        if not self._syncing:
            self._syncing = True
            target.verticalScrollBar().setValue(value)
            self._syncing = False
    
    def set_content(self, lines1, lines2, doc1_title, doc2_title, similarity):
        """设置对比内容 - 字词级精确比对"""
        text1 = '\n'.join(lines1)
        text2 = '\n'.join(lines2)
        
        added_count = 0
        deleted_count = 0
        
        cursor1 = self.text1.textCursor()
        cursor2 = self.text2.textCursor()
        
        try:
            matcher = SequenceMatcher(None, text1, text2)
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    self._append_text(cursor1, text1[i1:i2], None)
                    self._append_text(cursor2, text2[j1:j2], None)
                elif tag == 'delete':
                    self._append_text(cursor1, text1[i1:i2], 'deleted')
                    deleted_count += len(text1[i1:i2])
                elif tag == 'insert':
                    self._append_text(cursor2, text2[j1:j2], 'added')
                    added_count += len(text2[j1:j2])
                elif tag == 'replace':
                    self._append_text(cursor1, text1[i1:i2], 'deleted')
                    deleted_count += len(text1[i1:i2])
                    self._append_text(cursor2, text2[j1:j2], 'added')
                    added_count += len(text2[j1:j2])
        except Exception as e:
            self.text1.setText(f"比对出错: {str(e)}")
            self.text2.setText(f"比对出错: {str(e)}")
            return
        
        self.added_card.findChildren(QLabel)[0].setText(str(added_count))
        self.deleted_card.findChildren(QLabel)[0].setText(str(deleted_count))
        self.similarity_card.findChildren(QLabel)[0].setText(f"{similarity:.0%}")
        self.original_card.findChildren(QLabel)[0].setText(str(len(text1)))
        self.modified_card.findChildren(QLabel)[0].setText(str(len(text2)))
    
    def _append_text(self, cursor, text, style_type):
        """添加文本"""
        char_format = QTextCharFormat()
        
        if style_type == 'deleted':
            char_format.setBackground(QBrush(QColor('#fff1f0')))
            char_format.setForeground(QColor('#ff4d4f'))
            char_format.setFontStrikeOut(True)
        elif style_type == 'added':
            char_format.setBackground(QBrush(QColor('#fffbe6')))
            char_format.setForeground(QColor('#d4380d'))
        else:
            char_format.setForeground(QColor('#333'))
        
        cursor.setCharFormat(char_format)
        cursor.insertText(text)


class DiffViewerWidget(QWidget):
    """双栏对比视图 - 已弃用，保留兼容性"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        header = QHBoxLayout()
        
        self.doc1_label = QLabel("文档1")
        self.doc1_label.setStyleSheet("font-weight: bold; padding: 5px;")
        header.addWidget(self.doc1_label, 1)
        
        header.addWidget(QLabel("vs"), 0)
        
        self.doc2_label = QLabel("文档2")
        self.doc2_label.setStyleSheet("font-weight: bold; padding: 5px;")
        header.addWidget(self.doc2_label, 1)
        
        layout.addLayout(header)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.text1 = QTextEdit()
        self.text1.setReadOnly(True)
        self.text1.setStyleSheet("font-size: 12px;")
        splitter.addWidget(self.text1)
        
        self.text2 = QTextEdit()
        self.text2.setReadOnly(True)
        self.text2.setStyleSheet("font-size: 12px;")
        splitter.addWidget(self.text2)
        
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)
    
    def set_content(self, lines1, lines2, doc1_title, doc2_title):
        """设置对比内容"""
        self.doc1_label.setText(doc1_title or "文档1")
        self.doc2_label.setText(doc2_title or "文档2")
        
        differ = Differ()
        diff = list(differ.compare(lines1, lines2))
        
        cursor1 = self.text1.textCursor()
        cursor2 = self.text2.textCursor()
        
        i = j = 0
        for line in diff:
            if line.startswith('  '):
                self._append_colored_text(cursor1, line[2:] + '\n', QColor('black'))
                self._append_colored_text(cursor2, line[2:] + '\n', QColor('black'))
                i += 1
                j += 1
            elif line.startswith('- '):
                self._append_colored_text(cursor1, line[2:] + '\n', QColor('#ff4444'))
                i += 1
            elif line.startswith('+ '):
                self._append_colored_text(cursor2, line[2:] + '\n', QColor('#44aa44'))
                j += 1
            elif line.startswith('? '):
                pass
        
        while i < len(lines1):
            self._append_colored_text(cursor1, lines1[i] + '\n', QColor('black'))
            i += 1
        
        while j < len(lines2):
            self._append_colored_text(cursor2, lines2[j] + '\n', QColor('black'))
            j += 1
    
    def _append_colored_text(self, cursor, text, color):
        """添加带颜色的文本"""
        char_format = QTextCharFormat()
        char_format.setForeground(color)
        cursor.setCharFormat(char_format)
        cursor.insertText(text)


class ImprovedDiffViewerWidget(QWidget):
    """改进版双栏对比视图 - 带背景色高亮"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        doc1_container = QWidget()
        doc1_layout = QVBoxLayout(doc1_container)
        doc1_layout.setContentsMargins(5, 5, 5, 5)
        
        doc1_header = QLabel("原始稿")
        doc1_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 8px; background: #f5f7fa; border-radius: 4px;")
        doc1_layout.addWidget(doc1_header)
        
        self.text1 = QTextEdit()
        self.text1.setReadOnly(True)
        self.text1.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        doc1_layout.addWidget(self.text1)
        
        splitter.addWidget(doc1_container)
        
        doc2_container = QWidget()
        doc2_layout = QVBoxLayout(doc2_container)
        doc2_layout.setContentsMargins(5, 5, 5, 5)
        
        doc2_header = QLabel("修改稿")
        doc2_header.setStyleSheet("font-size: 16px; font-weight: bold; color: #333; padding: 8px; background: #f5f7fa; border-radius: 4px;")
        doc2_layout.addWidget(doc2_header)
        
        self.text2 = QTextEdit()
        self.text2.setReadOnly(True)
        self.text2.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #e8e8e8;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        doc2_layout.addWidget(self.text2)
        
        # 同步滚动
        self._syncing = False
        self.text1.verticalScrollBar().valueChanged.connect(lambda v: self.sync_scroll_to(self.text2, v))
        self.text2.verticalScrollBar().valueChanged.connect(lambda v: self.sync_scroll_to(self.text1, v))
        
        splitter.addWidget(doc2_container)
        
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)
    
    def set_content(self, lines1, lines2, doc1_title, doc2_title):
        """设置对比内容 - 逐字对比高亮"""
        differ = Differ()
        diff = list(differ.compare(lines1, lines2))
        
        cursor1 = self.text1.textCursor()
        cursor2 = self.text2.textCursor()
        
        i = j = 0
        for line in diff:
            if line.startswith('  '):
                self._append_line_with_bg(cursor1, line[2:] + '\n', None)
                self._append_line_with_bg(cursor2, line[2:] + '\n', None)
                i += 1
                j += 1
            elif line.startswith('- '):
                self._append_line_with_bg(cursor1, line[2:] + '\n', QColor('#fff1f0'))
                i += 1
            elif line.startswith('+ '):
                self._append_line_with_bg(cursor2, line[2:] + '\n', QColor('#f6ffed'))
                j += 1
            elif line.startswith('? '):
                pass
        
        while i < len(lines1):
            self._append_line_with_bg(cursor1, lines1[i] + '\n', None)
            i += 1
        
        while j < len(lines2):
            self._append_line_with_bg(cursor2, lines2[j] + '\n', None)
            j += 1
    
    def _append_line_with_bg(self, cursor, text, bg_color):
        """添加带背景色的行"""
        char_format = QTextCharFormat()
        if bg_color:
            char_format.setBackground(QBrush(bg_color))
        cursor.setCharFormat(char_format)
        cursor.insertText(text)
    
    def sync_scroll_to(self, target, value):
        """同步滚动到目标文本框"""
        if not self._syncing:
            self._syncing = True
            target.verticalScrollBar().setValue(value)
            self._syncing = False


class SmartAnalysisWidget(QWidget):
    """智能分析模块主界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("智能分析")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #333;
        """)
        layout.addWidget(title)
        
        tools_label = QLabel("分析工具")
        tools_label.setStyleSheet("font-size: 16px; color: #666;")
        layout.addWidget(tools_label)
        
        tools_widget = QWidget()
        tools_layout = QGridLayout(tools_widget)
        tools_layout.setSpacing(20)
        
        tools = [
            ("📊", "词频分析", "统计文档高频词汇，生成词云，可导出", self.on_word_freq),
            ("🔄", "文稿比对", "对比两篇文档的差异，双栏高亮显示", self.on_doc_compare),
            ("📝", "句式提取", "提取常用句式和排比句，可收藏到金句库", self.on_pattern_extract),
            ("🎓", "风格学习", "分析领导修改风格偏好，生成风格报告", self.on_style_learn),
            ("🔍", "相似度检测", "检测两篇文档的相似程度，显示相似段落", self.on_similarity),
            ("📋", "结构分析", "分析文档结构，提取大纲和关键句", self.on_structure),
        ]
        
        for i, (icon, name, desc, callback) in enumerate(tools):
            row = i // 3
            col = i % 3
            card = ToolCard(icon, name, desc)
            card.clicked.connect(callback)
            tools_layout.addWidget(card, row, col)
        
        layout.addWidget(tools_widget)
        
        self.result_area = QTabWidget()
        self.result_area.setVisible(False)
        layout.addWidget(self.result_area, 1)
        
        layout.addStretch()
    
    def on_word_freq(self):
        """词频分析"""
        dialog = DocumentSelectDialog(self, "选择要分析的文档")
        if dialog.exec_() == QDialog.Accepted:
            doc_id = dialog.get_selected_id()
            if doc_id:
                self.run_analysis('wordfreq', doc_id=doc_id)
    
    def on_doc_compare(self):
        """文稿比对"""
        dialog = DocumentCompareDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            doc1_id, doc2_id = dialog.get_selected_ids()
            if doc1_id and doc2_id:
                self.run_analysis('compare', doc1_id=doc1_id, doc2_id=doc2_id)
    
    def on_pattern_extract(self):
        """句式提取"""
        dialog = DocumentSelectDialog(self, "选择要分析的文档")
        if dialog.exec_() == QDialog.Accepted:
            doc_id = dialog.get_selected_id()
            if doc_id:
                self.run_analysis('pattern', doc_id=doc_id)
    
    def on_style_learn(self):
        """风格学习"""
        dialog = StyleLearnDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            original_id, revised_id = dialog.get_selected_ids()
            if original_id and revised_id:
                self.run_analysis('style', original_id=original_id, revised_id=revised_id)
    
    def on_similarity(self):
        """相似度检测"""
        dialog = DocumentCompareDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            doc1_id, doc2_id = dialog.get_selected_ids()
            if doc1_id and doc2_id:
                self.run_analysis('similarity', doc1_id=doc1_id, doc2_id=doc2_id)
    
    def on_structure(self):
        """结构分析"""
        dialog = DocumentSelectDialog(self, "选择要分析的文档")
        if dialog.exec_() == QDialog.Accepted:
            doc_id = dialog.get_selected_id()
            if doc_id:
                self.run_analysis('structure', doc_id=doc_id)
    
    def run_analysis(self, analysis_type, **kwargs):
        """运行分析"""
        if hasattr(self, 'worker') and self.worker is not None and self.worker.isRunning():
            QMessageBox.warning(self, "提示", "请等待当前分析完成")
            return
        
        self.worker = AnalysisWorker(analysis_type, **kwargs)
        self.worker.finished_signal.connect(self.on_analysis_finished)
        self.worker.start()
        
        self.progress = QProgressDialog("正在分析...", "取消", 0, 0, self)
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.canceled.connect(self.cancel_analysis)
        self.progress.show()
    
    def cancel_analysis(self):
        """取消分析"""
        if hasattr(self, 'worker') and self.worker is not None:
            self.worker.terminate()
            self.worker.wait()
            self.worker = None
    
    def on_analysis_finished(self, result):
        """分析完成回调"""
        self.progress.close()
        self.worker = None
        
        if 'error' in result:
            QMessageBox.warning(self, "分析失败", result['error'])
            return
        
        self.result_area.setVisible(True)
        self.result_area.clear()
        
        if 'word_freq' in result:
            self.show_word_freq_result(result)
        elif 'lines1' in result and 'lines2' in result:
            self.show_compare_result(result)
        elif 'sentences' in result and 'fixed_patterns' in result:
            self.show_pattern_result(result)
        elif 'similarity' in result and 'common_words' in result and 'similar_paragraphs' in result:
            self.show_similarity_result(result)
        elif 'added_words' in result:
            self.show_style_result(result)
        elif 'outline' in result:
            self.show_structure_result(result)
    
    def show_word_freq_result(self, result):
        """显示词频分析结果 - 改进布局"""
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 左侧：词云
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        wordcloud_widget = WordCloudWidget()
        wordcloud_widget.generate_wordcloud(result['word_freq'])
        wordcloud_widget.setStyleSheet("background-color: white; border: 1px solid #e8e8e8; border-radius: 8px;")
        left_layout.addWidget(wordcloud_widget, 1)
        
        main_layout.addWidget(left_widget, 1)
        
        # 右侧：统计和词频表
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(15)
        
        # 统计概览 - 横向排列
        stats_widget = QWidget()
        stats_widget.setStyleSheet("background-color: white; border: 1px solid #e8e8e8; border-radius: 8px; padding: 10px;")
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(10, 5, 10, 5)
        stats_layout.setSpacing(30)
        
        def create_stat_box(label, value):
            box = QWidget()
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(0, 0, 0, 0)
            box_layout.setSpacing(3)
            
            value_label = QLabel(str(value))
            value_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1890ff;")
            value_label.setAlignment(Qt.AlignCenter)
            
            name_label = QLabel(label)
            name_label.setStyleSheet("font-size: 12px; color: #666;")
            name_label.setAlignment(Qt.AlignCenter)
            
            box_layout.addWidget(value_label)
            box_layout.addWidget(name_label)
            return box
        
        stats_layout.addWidget(create_stat_box("分析文档数", 1))
        stats_layout.addWidget(create_stat_box("总词数", result['total_words']))
        stats_layout.addWidget(create_stat_box("不重复词", result['unique_words']))
        stats_layout.addStretch()
        
        right_layout.addWidget(stats_widget)
        
        # 高频词 TOP 20 - 更大的表格
        top_words_title = QLabel("高频词 TOP 20")
        top_words_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #333;")
        right_layout.addWidget(top_words_title)
        
        table_widget = QWidget()
        table_widget.setStyleSheet("background-color: white; border: 1px solid #e8e8e8; border-radius: 8px;")
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(10, 10, 10, 10)
        
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["词汇", "次数", "占比"])
        table.setRowCount(min(20, len(result['word_freq'])))
        table.verticalHeader().setVisible(False)
        table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 8px 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QHeaderView::section {
                background-color: transparent;
                border: none;
                border-bottom: 2px solid #1890ff;
                padding: 8px 8px;
                font-weight: bold;
                color: #333;
            }
        """)
        
        total_freq = sum(f for _, f in result['word_freq'])
        
        for i, (word, freq) in enumerate(result['word_freq'][:20]):
            table.setItem(i, 0, QTableWidgetItem(word))
            
            freq_item = QTableWidgetItem(str(freq))
            freq_item.setTextAlignment(Qt.AlignCenter)
            table.setItem(i, 1, freq_item)
            
            percentage = (freq / total_freq * 100) if total_freq > 0 else 0
            table.setItem(i, 2, QTableWidgetItem(f"{percentage:.2f}%"))
        
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        table_layout.addWidget(table)
        right_layout.addWidget(table_widget, 1)
        
        main_layout.addWidget(right_widget, 1)
        
        self.result_area.addTab(main_widget, "词频分析结果")
    
    def export_word_freq(self, result):
        """导出词频"""
        filename, _ = QFileDialog.getSaveFileName(self, "导出词频", "", "CSV文件 (*.csv);;文本文件 (*.txt)")
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8-sig') as f:
                    f.write("排名,词汇,频次\n")
                    for i, (word, freq) in enumerate(result['word_freq']):
                        f.write(f"{i+1},{word},{freq}\n")
                QMessageBox.information(self, "成功", "导出成功！")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"导出失败: {str(e)}")
    
    def show_compare_result(self, result):
        """显示比对结果 - 紧凑版"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("文稿比对")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        diff_viewer = CompactDiffViewerWidget()
        diff_viewer.set_content(
            result['lines1'],
            result['lines2'],
            result['doc1_title'],
            result['doc2_title'],
            result['similarity']
        )
        layout.addWidget(diff_viewer, 1)
        
        self.result_area.addTab(widget, "文稿比对结果")
    
    def show_pattern_result(self, result):
        """显示句式提取结果"""
        widget = QTabWidget()
        
        if result['parallel_sentences']:
            parallel_widget = QWidget()
            parallel_layout = QVBoxLayout(parallel_widget)
            parallel_list = QListWidget()
            for s1, s2, s3 in result['parallel_sentences']:
                item = QListWidgetItem(f"排比句组:\n  1. {s1}\n  2. {s2}\n  3. {s3}")
                parallel_list.addItem(item)
            parallel_layout.addWidget(parallel_list)
            widget.addTab(parallel_widget, "排比句")
        
        if result['fixed_patterns']:
            pattern_widget = QWidget()
            pattern_layout = QVBoxLayout(pattern_widget)
            pattern_list = QListWidget()
            for p in result['fixed_patterns']:
                item = QListWidgetItem(f"{p['name']} (出现{p['count']}次)")
                pattern_list.addItem(item)
                for example in p['examples'][:5]:
                    pattern_list.addItem(f"  - {example}")
            pattern_layout.addWidget(pattern_list)
            widget.addTab(pattern_widget, "固定搭配")
        
        if result['opening_patterns']:
            opening_widget = QWidget()
            opening_layout = QVBoxLayout(opening_widget)
            opening_list = QListWidget()
            for sent in result['opening_patterns']:
                opening_list.addItem(sent)
            opening_layout.addWidget(opening_list)
            widget.addTab(opening_widget, "开头句式")
        
        if result['closing_patterns']:
            closing_widget = QWidget()
            closing_layout = QVBoxLayout(closing_widget)
            closing_list = QListWidget()
            for sent in result['closing_patterns']:
                closing_list.addItem(sent)
            closing_layout.addWidget(closing_list)
            widget.addTab(closing_widget, "结尾句式")
        
        self.result_area.addTab(widget, "句式提取结果")
    
    def show_quote_context_menu(self, pos, list_widget, doc_id):
        """显示金句收藏菜单"""
        item = list_widget.itemAt(pos)
        if not item:
            return
        
        menu = QMenu(self)
        add_action = QAction("添加到金句库", self)
        add_action.triggered.connect(lambda: self.add_to_quotes(item.text(), doc_id))
        menu.addAction(add_action)
        menu.exec_(list_widget.mapToGlobal(pos))
    
    def add_to_quotes(self, content, doc_id):
        """添加到金句库 - 改进版对话框"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLabel, QTextEdit, QComboBox, QLineEdit, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("添加到金句库")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # 去掉问号
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        form = QFormLayout()
        
        # 金句内容（只读）
        content_edit = QTextEdit()
        content_edit.setPlainText(content)
        content_edit.setMaximumHeight(100)
        content_edit.setReadOnly(True)
        form.addRow("金句内容:", content_edit)
        
        # 分类下拉框
        category_combo = QComboBox()
        category_combo.setEditable(True)  # 允许输入新分类
        category_combo.addItem("其他", "")
        category_combo.addItem("开头句", "开头句")
        category_combo.addItem("结尾句", "结尾句")
        category_combo.addItem("过渡句", "过渡句")
        category_combo.addItem("排比句", "排比句")
        category_combo.addItem("固定搭配", "固定搭配")
        category_combo.addItem("强调句", "强调句")
        category_combo.addItem("总结句", "总结句")
        category_combo.addItem("对策句", "对策句")
        category_combo.addItem("成效句", "成效句")
        form.addRow("分类:", category_combo)
        
        # 标签输入
        tags_edit = QLineEdit()
        tags_edit.setPlaceholderText("多个标签用逗号分隔，如：党建,经济,发展")
        form.addRow("标签:", tags_edit)
        
        layout.addLayout(form)
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #1890ff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 20px;
            }
            QPushButton:hover {
                background-color: #40a9ff;
            }
        """)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                category = category_combo.currentText().strip()
                tags = tags_edit.text().strip()
                
                db.add_quote(
                    content=content,
                    document_id=doc_id,
                    category=category if category else None,
                    tags=tags if tags else None
                )
                QMessageBox.information(self, "成功", "已添加到金句库！")
            except Exception as e:
                QMessageBox.warning(self, "错误", f"添加失败: {str(e)}")
    
    def show_similarity_result(self, result):
        """显示相似度结果 - 修复布局"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        title = QLabel("相似度检测")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(title)
        
        info_widget = QWidget()
        info_widget.setStyleSheet("background-color: white; border: 1px solid #e8e8e8; border-radius: 8px;")
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(30, 30, 30, 30)
        info_layout.setSpacing(20)
        
        doc_info = QLabel(f"{result['doc1_title']}\n与\n{result['doc2_title']}")
        doc_info.setStyleSheet("font-size: 16px; color: #666;")
        doc_info.setAlignment(Qt.AlignCenter)
        doc_info.setWordWrap(True)
        info_layout.addWidget(doc_info)
        
        # 相似度大数字显示
        similarity_value = int(result['similarity'] * 100)
        similarity = QLabel(f"{similarity_value}%")
        similarity.setStyleSheet("""
            font-size: 72px;
            font-weight: bold;
            color: #1890ff;
            padding: 20px;
        """)
        similarity.setAlignment(Qt.AlignCenter)
        similarity.setMinimumHeight(120)
        info_layout.addWidget(similarity)
        
        similarity_label = QLabel("文档相似度")
        similarity_label.setStyleSheet("font-size: 14px; color: #999;")
        similarity_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(similarity_label)
        
        layout.addWidget(info_widget)
        layout.addStretch()
        
        self.result_area.addTab(widget, "相似度检测结果")
    
    def show_style_result(self, result):
        """显示风格学习结果"""
        widget = QTabWidget()
        
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        
        info = QLabel(f"原始稿: {result['original_title']}\n修改稿: {result['revised_title']}")
        info.setStyleSheet("font-size: 14px; color: #666; padding: 10px; background: #f5f7fa; border-radius: 4px;")
        summary_layout.addWidget(info)
        
        if result['style_recommendations']:
            rec_label = QLabel("风格分析结论:")
            rec_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 15px;")
            summary_layout.addWidget(rec_label)
            
            for rec in result['style_recommendations']:
                rec_item = QLabel(f"• {rec}")
                rec_item.setStyleSheet("padding: 5px; color: #333;")
                summary_layout.addWidget(rec_item)
        
        summary_layout.addStretch()
        widget.addTab(summary_widget, "风格概览")
        
        if result['added_words']:
            added_widget = QWidget()
            added_layout = QVBoxLayout(added_widget)
            added_table = QTableWidget()
            added_table.setColumnCount(2)
            added_table.setHorizontalHeaderLabels(["新增词汇", "频次"])
            added_table.setRowCount(len(result['added_words']))
            
            for i, (word, count) in enumerate(result['added_words']):
                added_table.setItem(i, 0, QTableWidgetItem(word))
                added_table.setItem(i, 1, QTableWidgetItem(str(count)))
            
            added_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            added_layout.addWidget(added_table)
            widget.addTab(added_widget, "新增词汇")
        
        if result['removed_words']:
            removed_widget = QWidget()
            removed_layout = QVBoxLayout(removed_widget)
            removed_table = QTableWidget()
            removed_table.setColumnCount(2)
            removed_table.setHorizontalHeaderLabels(["删除词汇", "频次"])
            removed_table.setRowCount(len(result['removed_words']))
            
            for i, (word, count) in enumerate(result['removed_words']):
                removed_table.setItem(i, 0, QTableWidgetItem(word))
                removed_table.setItem(i, 1, QTableWidgetItem(str(count)))
            
            removed_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            removed_layout.addWidget(removed_table)
            widget.addTab(removed_widget, "删除词汇")
        
        if result['emphasized_words']:
            emphasized_widget = QWidget()
            emphasized_layout = QVBoxLayout(emphasized_widget)
            emphasized_table = QTableWidget()
            emphasized_table.setColumnCount(4)
            emphasized_table.setHorizontalHeaderLabels(["强调词汇", "原稿频次", "修改稿频次", "变化倍数"])
            emphasized_table.setRowCount(len(result['emphasized_words']))
            
            for i, (word, orig, rev, ratio) in enumerate(result['emphasized_words']):
                emphasized_table.setItem(i, 0, QTableWidgetItem(word))
                emphasized_table.setItem(i, 1, QTableWidgetItem(str(orig)))
                emphasized_table.setItem(i, 2, QTableWidgetItem(str(rev)))
                emphasized_table.setItem(i, 3, QTableWidgetItem(f"{ratio:.1f}x"))
            
            emphasized_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            emphasized_layout.addWidget(emphasized_table)
            widget.addTab(emphasized_widget, "强调词汇")
        
        self.result_area.addTab(widget, "风格学习结果")
    
    def show_structure_result(self, result):
        """显示结构分析结果"""
        widget = QTabWidget()
        
        summary_widget = QWidget()
        summary_layout = QVBoxLayout(summary_widget)
        
        info = QLabel(f"文档: {result['doc_title']} | 总行数: {result['total_lines']} | 段落数: {result['total_paragraphs']} | 标题数: {result['total_headings']}")
        info.setStyleSheet("font-size: 14px; color: #666; padding: 10px; background: #f5f7fa; border-radius: 4px;")
        summary_layout.addWidget(info)
        summary_layout.addStretch()
        widget.addTab(summary_widget, "结构概览")
        
        if result['outline']:
            outline_widget = QWidget()
            outline_layout = QVBoxLayout(outline_widget)
            
            outline_tree = QTreeWidget()
            outline_tree.setHeaderLabel("文档大纲")
            
            root = QTreeWidgetItem(outline_tree, [result['doc_title']])
            
            current_items = {0: root}
            
            for item in result['outline']:
                level = item['level']
                text = item['text']
                
                parent_level = level - 1
                while parent_level not in current_items and parent_level > 0:
                    parent_level -= 1
                
                parent = current_items.get(parent_level, root)
                tree_item = QTreeWidgetItem(parent, [text])
                current_items[level] = tree_item
            
            root.setExpanded(True)
            outline_layout.addWidget(outline_tree)
            widget.addTab(outline_widget, "文档大纲")
        
        if result['key_sentences']:
            key_widget = QWidget()
            key_layout = QVBoxLayout(key_widget)
            
            key_list = QListWidget()
            for sent in result['key_sentences']:
                item = QListWidgetItem(sent)
                item.setData(Qt.UserRole, sent)
                key_list.addItem(item)
            
            key_list.setContextMenuPolicy(Qt.CustomContextMenu)
            key_list.customContextMenuRequested.connect(
                lambda pos: self.show_quote_context_menu(pos, key_list, None)
            )
            
            key_layout.addWidget(key_list)
            widget.addTab(key_widget, "关键句")
        
        self.result_area.addTab(widget, "结构分析结果")


class DocumentSelectDialog(QDialog):
    """文档选择对话框"""
    
    def __init__(self, parent=None, title="选择文档"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(500, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        search_layout = QHBoxLayout()
        self.search_input = QTextEdit()
        self.search_input.setMaximumHeight(30)
        self.search_input.setPlaceholderText("搜索文档...")
        self.search_input.textChanged.connect(self.filter_documents)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        
        self.documents = db.get_all_documents()
        self.refresh_list()
        
        layout.addWidget(self.list_widget, 1)
        
        buttons = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("background-color: #1890ff; color: white; padding: 8px 20px;")
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)
    
    def refresh_list(self):
        self.list_widget.clear()
        for doc in self.documents:
            item = QListWidgetItem(f"{doc['title'] or '未命名'} ({doc['file_type'] or '未知'})")
            item.setData(Qt.UserRole, doc['id'])
            self.list_widget.addItem(item)
    
    def filter_documents(self):
        text = self.search_input.toPlainText().lower()
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text not in item.text().lower())
    
    def get_selected_id(self):
        item = self.list_widget.currentItem()
        return item.data(Qt.UserRole) if item else None


class DocumentCompareDialog(QDialog):
    """文档对比选择对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择两篇文档进行对比")
        self.setMinimumSize(600, 700)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Vertical)
        
        doc1_widget = QWidget()
        doc1_layout = QVBoxLayout(doc1_widget)
        doc1_layout.addWidget(QLabel("选择第一篇文档:"))
        self.list1 = QListWidget()
        self.list1.setSelectionMode(QListWidget.SingleSelection)
        doc1_layout.addWidget(self.list1)
        splitter.addWidget(doc1_widget)
        
        doc2_widget = QWidget()
        doc2_layout = QVBoxLayout(doc2_widget)
        doc2_layout.addWidget(QLabel("选择第二篇文档:"))
        self.list2 = QListWidget()
        self.list2.setSelectionMode(QListWidget.SingleSelection)
        doc2_layout.addWidget(self.list2)
        splitter.addWidget(doc2_widget)
        
        splitter.setSizes([350, 350])
        layout.addWidget(splitter, 1)
        
        documents = db.get_all_documents()
        for doc in documents:
            text = f"{doc['title'] or '未命名'} ({doc['file_type'] or '未知'})"
            
            item1 = QListWidgetItem(text)
            item1.setData(Qt.UserRole, doc['id'])
            self.list1.addItem(item1)
            
            item2 = QListWidgetItem(text)
            item2.setData(Qt.UserRole, doc['id'])
            self.list2.addItem(item2)
        
        buttons = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("background-color: #1890ff; color: white; padding: 8px 20px;")
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)
    
    def get_selected_ids(self):
        item1 = self.list1.currentItem()
        item2 = self.list2.currentItem()
        return (
            item1.data(Qt.UserRole) if item1 else None,
            item2.data(Qt.UserRole) if item2 else None
        )


class StyleLearnDialog(QDialog):
    """风格学习对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("领导风格学习 - 选择原始稿和修改稿")
        self.setMinimumSize(600, 700)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Vertical)
        
        original_widget = QWidget()
        original_layout = QVBoxLayout(original_widget)
        original_layout.addWidget(QLabel("选择原始稿:"))
        self.original_list = QListWidget()
        self.original_list.setSelectionMode(QListWidget.SingleSelection)
        original_layout.addWidget(self.original_list)
        splitter.addWidget(original_widget)
        
        revised_widget = QWidget()
        revised_layout = QVBoxLayout(revised_widget)
        revised_layout.addWidget(QLabel("选择修改稿:"))
        self.revised_list = QListWidget()
        self.revised_list.setSelectionMode(QListWidget.SingleSelection)
        revised_layout.addWidget(self.revised_list)
        splitter.addWidget(revised_widget)
        
        splitter.setSizes([350, 350])
        layout.addWidget(splitter, 1)
        
        documents = db.get_all_documents()
        for doc in documents:
            text = f"{doc['title'] or '未命名'} ({doc['file_type'] or '未知'})"
            
            item1 = QListWidgetItem(text)
            item1.setData(Qt.UserRole, doc['id'])
            self.original_list.addItem(item1)
            
            item2 = QListWidgetItem(text)
            item2.setData(Qt.UserRole, doc['id'])
            self.revised_list.addItem(item2)
        
        buttons = QHBoxLayout()
        ok_btn = QPushButton("开始分析")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("background-color: #1890ff; color: white; padding: 8px 20px;")
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(ok_btn)
        layout.addLayout(buttons)
    
    def get_selected_ids(self):
        item1 = self.original_list.currentItem()
        item2 = self.revised_list.currentItem()
        return (
            item1.data(Qt.UserRole) if item1 else None,
            item2.data(Qt.UserRole) if item2 else None
        )
